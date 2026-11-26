"""Privileged reference controller: reads the cell's ground truth, never the cameras.

Track and belt alike: the right gripper waits open over the part's lane, fingers either side of it, approach along the
surface normal; it closes as the part's centre arrives, lifts, carries the part over the tote, opens, and goes back.
All geometry is world frame; joint targets come from the URDF kinematics in kin.py (base frame = base_link)."""
from __future__ import annotations
import math
import numpy as np
import kin

HZ = 30
MAX_STEP = 0.07            # rad per control step, joint target slew
PICK_SIDE = 0.385      # where the right arm takes parts best: metres to the right of the base (the lane of the tuning shift)
SL = {"base": slice(0, 3), "trunk": slice(3, 7), "arm_left": slice(7, 14), "gl": 14, "arm_right": slice(15, 22), "gr": 22}
PRO = {"arm_left": slice(3, 10), "arm_right": slice(28, 35), "trunk": slice(53, 57)}


def rot(q):
    x, y, z, w = q
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


class Oracle:
    def __init__(self, s_catch=0.32, lead_s=0.10, clear=0.012, s_min=0.10, settle=3):
        self.arm = kin.Arm("right"); self.s_catch, self.lead, self.clear, self.s_min, self.settle = s_catch, lead_s, clear, s_min, settle; self.t_close = 0
        self.tool = None; self.state = "init"; self.t_state = 0; self.target_q = None; self.log = []
        self.q_pref = np.r_[0.3, -0.6, -0.3, 0.0, 0.0, -0.3, 0.0, -1.2, 0.0, 0.0, 0.0]; self.diag = {}; self.grip = 1.0; self.event = -1; self.fk_err = None; self.reach = 0.045   # fingertip beyond the finger links' origin

    # ---- frames
    def _base(self, tr):
        Rb = rot(tr["base_quat"]); return Rb, np.array(tr["base_pos"])

    def _q(self, proprio):
        return np.r_[proprio[PRO["trunk"]], proprio[PRO["arm_right"]]]

    def _calibrate(self, tr, proprio):
        """The URDF model and the simulator's links differ by a fixed offset (6 cm measured), so the controller servoes
        on the measured gripper pose from truth; the model only supplies the Jacobian. Here: the constant rotation
        between the simulator's eef link and the URDF gripper link."""
        Rb, pb = self._base(tr); q = self._q(proprio)
        p, R, _ = self.arm.fk(q); pw = Rb @ p + pb
        self.fk_err = float(np.linalg.norm(pw - np.array(tr["eef_right_pos"])))
        self.R_off = (Rb @ R).T @ rot(tr["eef_right_quat"])
        self.tool = np.array([0.0, 0.0, -0.125])
        Rg0 = rot(tr["eef_right_quat"]) @ self.R_off.T
        if tr.get("finger_low_right") is not None and Rg0[2, 2] > 0.97:      # gripper pointing straight down at start
            self.reach = float(np.clip(tr["fingers_right"][2] - tr["finger_low_right"], 0.02, 0.12))
        self.log.append({"reach": round(self.reach, 4), "fk_vs_eef_m": round(self.fk_err, 4), "offset_world": (np.array(tr["eef_right_pos"]) - pw).round(4).tolist()})

    def _measured(self, tr):
        """Gripper rotation (URDF gripper-link convention) and tool point (between the fingertips), world frame."""
        Rg = rot(tr["eef_right_quat"]) @ self.R_off.T
        return np.array(tr["fingers_right"]) - Rg[:, 2] * self.reach, Rg

    def _servo(self, tr, q_now, p_world, R_world, gain=0.6):
        """Resolved-rate step toward the pose: measured error, model Jacobian. Returns new joint targets and the error."""
        Rb, _ = self._base(tr); tp, Rm = self._measured(tr)
        flip = R_world @ np.diag([-1.0, -1.0, 1.0])       # the gripper is symmetric: turned half a turn about its approach axis it grasps the same
        if np.trace(flip @ Rm.T) > np.trace(R_world @ Rm.T): R_world = flip
        e_p = Rb.T @ (np.asarray(p_world) - tp); Re = (Rb.T @ R_world) @ (Rb.T @ Rm).T
        e_r = 0.5 * np.array([Re[2, 1] - Re[1, 2], Re[0, 2] - Re[2, 0], Re[1, 0] - Re[0, 1]])
        J, _, _ = self.arm.jacobian(q_now, self.tool); free = np.ones(11, bool); free[3] = False
        A = np.r_[J[:3], 0.3 * J[3:]][:, free]; err = np.r_[np.clip(e_p, -0.15, 0.15), 0.3 * e_r]
        Ap = A.T @ np.linalg.inv(A @ A.T + 0.04 ** 2 * np.eye(6)); dq = Ap @ err
        # Null-space pull toward a comfortable posture, so the local servo does not creep into joint limits.
        dq = dq + (np.eye(A.shape[1]) - np.linalg.pinv(A, rcond=1e-3) @ A) @ (0.08 * (self.q_pref[free] - q_now[free]))   # exact projector: no leak into the task
        q = q_now.copy(); q[free] = np.clip(q_now[free] + np.clip(gain * dq, -MAX_STEP, MAX_STEP), self.arm.lo[free], self.arm.hi[free])
        return q, float(np.linalg.norm(e_p))

    def _solve(self, tr, q_now, p_world, R_world):
        """Global IK (model frame) from a few seeds; used only for large moves."""
        Rb, pb = self._base(tr); p = Rb.T @ (np.asarray(p_world) - pb); R = Rb.T @ R_world
        free = np.ones(11, bool); free[3] = False; best = None
        for seed in (np.r_[0.3, -0.6, -0.3, 0, 0, 0, 0, -1.2, 0, 0, 0], np.r_[0.6, -1.2, -0.6, 0, 0, 0, 0, -1.0, 0, 0, 0], q_now):
            q, err = self.arm.ik(np.clip(seed, self.arm.lo, self.arm.hi), p, R, tool=self.tool, free=free, iters=150)
            margin = float(np.minimum(q - self.arm.lo, self.arm.hi - q)[4:].min())          # stay off the arm's joint limits
            cost = err * 50 + (0.5 if margin < 0.05 else 0.0)
            if best is None or cost < best[0]: best = (cost, q, err)
        return best[1], best[2]

    def log_has_event(self):
        return bool(self.log) and self.log[-1].get("event") == self.event

    def _go(self, name):
        if name != self.state: self.state, self.t_state = name, 0

    # ---- one control step
    def act(self, obs, tr):
        proprio = np.asarray(obs["proprio"], float); q_now = self._q(proprio)
        if self.tool is None: self._calibrate(tr, proprio); self.target_q = q_now.copy(); self.home_left = proprio[PRO["arm_left"]].copy()
        self.t_state += 1
        fwd, left, up = np.array(tr["fwd"]), np.array(tr["left"]), np.array(tr["up_chute"])
        low = np.array(tr["low_end"]); belt = tr["station"] == "belt"
        along_axis = fwd if belt else up
        n = np.cross(along_axis, left); n = n / np.linalg.norm(n) * (1 if np.cross(along_axis, left)[2] > 0 else -1)
        Rg = np.stack([np.cross(left, n), left, n], axis=1)          # gripper x, y (opening, across the lane), z (away from surface)
        if tr["phase"] in ("staged", "live") and tr["event"] != self.event:
            self.event = tr["event"]; self._go("wait"); self.grip = 1.0; self.catch_err = None; self.stall = 0; self._gap = 9.0; self.reopen_until = 0
        if self.state in ("init",): self._go("wait")
        want = None
        if self.state == "wait" and tr["phase"] not in ("staged", "live"):
            want = low + along_axis * self.s_catch + left * getattr(self, "last_lane", 0.0) + n * (self.clear + 0.03)
        if self.state in ("wait", "follow") and tr["phase"] in ("staged", "live"):
            # Tracking grasp: wait at s_max; once the part passes, travel down the lane with it (target = the part's own
            # position, led by the servo lag) so that the fingers close on a part that is at rest relative to them.
            pos = np.array(tr["pos"]); box = tr.get("aabb")
            if box is not None: pos = 0.5 * (np.array(box[0]) + np.array(box[1]))       # geometric centre, not the mesh origin (mug, drill)
            lane = float((pos - low) @ left); self.last_lane = lane
            s = float((pos - low) @ along_axis); v = -float(np.array(tr["vel"]) @ along_axis)
            Rp = rot(tr["quat"]); width = 2.0 * float(np.abs(Rp.T @ left) @ (np.array(tr["size"]) / 2.0)); self.width = width
            # The arm follows a moving target with a steady lag (joint controller, step limits): 2 to 4 cm at these speeds,
            # which is the whole alignment tolerance. An integral term on the measured along-lane error removes it.
            if self.state == "follow":
                lag = float((pos - self._measured(tr)[0]) @ along_axis)                 # negative: the hand trails the part
                self.i_along = float(np.clip(getattr(self, "i_along", 0.0) + 0.12 * lag, -0.08, 0.08))
            else: self.i_along = 0.5 * getattr(self, "i_along", 0.0)
            s_ref = float(np.clip(s - max(v, 0.0) * self.lead + self.i_along, self.s_min, self.s_catch))
            height = 2.0 * float(np.abs(Rp.T @ n) @ (np.array(tr["size"]) / 2.0))        # the part's extent off the surface
            length = 2.0 * float(np.abs(Rp.T @ along_axis) @ (np.array(tr["size"]) / 2.0))
            # Extents from the item's own box and its orientation: the world-aligned bounding box overstated the width
            # of every part (job 62685458), so it is used for the centre only.
            # Which way to hold it: across the lane if it fits between the fingers, else along the lane, else by the rim
            # (open containers), else leave it alone: fingers set down on a part too wide for them pinned it (jam).
            # Parts lie at any yaw (they turn as they slide; on the belt they are set down at random). Hold a part across its
            # own narrow horizontal axis: take the two body axes nearest the surface plane, decide which carries which
            # size by comparing with the measured bounding box, and turn the gripper's opening axis onto the narrow one.
            sz = np.array(tr["size"], float); hor = np.argsort(np.abs(Rp.T @ n))[:2]; u = [Rp[:, k] - n * float(Rp[:, k] @ n) for k in hor]; u = [v_ / (np.linalg.norm(v_) + 1e-9) for v_ in u]
            dims = [float(sz[hor[0]]), float(sz[hor[1]])]
            if box is not None:
                ext = np.array(box[1]) - np.array(box[0]); m_lat = float(np.abs(left) @ ext); m_al = float(np.abs(along_axis) @ ext)
                def miss(d): return abs(abs(u[0] @ left) * d[0] + abs(u[1] @ left) * d[1] - m_lat) + abs(abs(u[0] @ along_axis) * d[0] + abs(u[1] @ along_axis) * d[1] - m_al)
                if miss(dims[::-1]) < miss(dims): dims = dims[::-1]
            k = int(np.argmin(dims)); g_axis = u[k]; width = dims[k]; length = dims[1 - k]
            mode = "rim" if tr["item"] == "024_bowl" else "skip" if width > 0.118 else "narrow"
            if mode == "narrow": Rg = np.stack([np.cross(g_axis, n), g_axis, n], axis=1)
            yaw_off = float(np.degrees(np.arctan2(abs(g_axis @ along_axis), abs(g_axis @ left))))
            if mode == "rim": pos = pos + left * (0.5 * width - 0.004); lane = float((pos - low) @ left); width = 0.01
            low_tip = max(self.clear, height - (0.03 if mode == "rim" else 0.065))           # fingertips as low as the fingers' length allows
            # Hover clear of the part's top while waiting and synchronising (a low gripper stopped tall parts: jam),
            # then come down onto it while travelling with it.
            down = self.state == "follow" and self.t_state >= self.settle and mode != "skip"
            self.tip_h = low_tip if down else height + 0.04
            want = low + along_axis * s_ref + left * lane + n * self.tip_h
            if tr["phase"] == "live" and self.state == "wait" and s - max(v, 0.0) * self.lead <= self.s_catch: self._go("follow")
            if self.state == "follow":
                ts_close = max(1, int(round((0.127 - width) / 0.5 * HZ)))                 # steps the fingers need to reach the part
                tip_now = float((self._measured(tr)[0] - low) @ n)
                off = pos - self._measured(tr)[0]; aligned = abs(float(off @ along_axis)) < 0.03 and abs(float(off @ left)) < 0.025
                d = self.diag.setdefault(self.event, {"item": tr["item"], "follow_steps": 0, "min_along": 9.0, "min_lat": 9.0, "min_tip_above": 9.0, "v": round(v, 2), "s_start": round(s, 2), "mode": mode, "w": round(width, 3), "h": round(height, 3), "yaw": round(yaw_off)})
                d["follow_steps"] += 1; d["min_along"] = round(min(d["min_along"], abs(float(off @ along_axis))), 3); d["min_lat"] = round(min(d["min_lat"], abs(float(off @ left))), 3)
                d["min_tip_above"] = round(min(d["min_tip_above"], tip_now - low_tip), 3); d["s_end"] = round(s, 2)
                if self.grip > 0 and self.t_state >= self.settle and self.t_state >= getattr(self, "reopen_until", 0) and tip_now <= low_tip + 0.012 and aligned and mode != "skip":
                    self.grip = -1.0; self.t_close = self.t_state
                    self.log.append({"event": self.event, "item": tr["item"], "close_s": round(s, 3), "v": round(v, 3), "lane": round(lane, 3), "width": round(width, 3), "height": round(height, 3),
                                     "ik_err": self.catch_err, "tool_minus_part": (self._measured(tr)[0] - pos).round(3).tolist()})
                # Lift only once the fingers have stopped on the part (the gap no longer shrinks): lifting while they
                # still close let the part slip out (seen 2026-11-25). A gap at its minimum means nothing was caught.
                gap = float(tr.get("finger_gap_right", 0.0)); stalled = self.grip < 0 and abs(gap - getattr(self, "_gap", 9.0)) < 0.0015
                self.stall = getattr(self, "stall", 0) + 1 if stalled else 0; self._gap = gap
                att = tr.get("attached_right")
                # Lift only once the simulator has attached the part to the hand (both fingers on it for 0.3 s): parts lifted
                # on finger pressure alone were lost or thrown on the way to the tote (anchor run of 2026-11-25).
                if self.grip < 0 and att: self.log[-1]["grip_gap"] = round(gap, 3); self.log[-1]["attached"] = True; self._go("lift")
                elif self.grip < 0 and att is None and self.stall >= 5 and gap > 0.0295: self.log[-1]["grip_gap"] = round(gap, 3); self._go("lift")
                elif self.grip < 0 and ((self.stall >= 3 and gap <= 0.0295) or self.t_state >= self.t_close + (24 if att is not None else 16)):
                    # Closed on nothing: open again and keep travelling with the part for another try (parts are slow).
                    self.log[-1]["retries"] = self.log[-1].get("retries", 0) + 1
                    if s_ref > self.s_min + 0.03 and self.log[-1]["retries"] <= 3: self.grip = 1.0; self.reopen_until = self.t_state + 7; self.stall = 0; self._gap = 9.0
                    else: self.log[-1]["grip_gap"] = round(gap, 3); self._go("lift")
                if s_ref <= self.s_min + 1e-6 and self.grip > 0 and not self.log_has_event(): self.log.append({"event": self.event, "item": tr["item"], "close_s": round(s, 3), "v": round(v, 3), "width": round(width, 3), "last_chance": True})
                if s_ref <= self.s_min + 1e-6 and self.grip > 0 and mode != "skip": self.grip = -1.0; self.t_close = self.t_state
        elif self.state == "lift":
            want = np.array(tr["fingers_right"]); want = np.array([want[0], want[1], max(want[2], low[2] + 0.22)])
            Rg = np.eye(3) @ self._yaw_R(tr)
            if self.t_state > 22: self._go("carry")
        elif self.state == "carry":
            tote = np.array(tr["tote"]); want = tote + np.array([0, 0, 0.36]); Rg = self._yaw_R(tr)
            near = float(np.linalg.norm((np.array(tr["fingers_right"]) - want)[:2])) < 0.06
            if (near and self.t_state > 8) or self.t_state > 70: self.grip = 1.0; self._go("drop")
        elif self.state == "drop":
            tote = np.array(tr["tote"]); want = tote + np.array([0, 0, 0.36]); Rg = self._yaw_R(tr)
            if self.t_state > 12: self._go("wait")
        if want is not None:
            slow = self.state in ("lift", "carry")                       # B. gentle with a part in the fingers
            tp, _ = self._measured(tr); far = float(np.linalg.norm(np.asarray(want) - tp))
            # The local servo is the proven controller. When the hand is far away (it got stuck after some events),
            # first return in joint space to the posture in which the waiting pose was last reached, then servo.
            q_ready = getattr(self, "q_ready", None)
            if far > 0.25 and q_ready is not None and self.state == "wait":
                self.target_q = q_now + np.clip(q_ready - q_now, -MAX_STEP, MAX_STEP); err = far
            else:
                self.target_q, err = self._servo(tr, q_now, want, Rg, gain=0.35 if slow else 0.6)
            if self.state == "wait" and err < 0.008: self.q_ready = q_now.copy()
            if self.state in ("wait", "follow"): self.catch_err = round(float(err), 4)
        row = np.zeros(23); row[SL["trunk"]] = self.target_q[:4]; row[SL["arm_right"]] = self.target_q[4:]
        # The robot is mobile, and the right arm takes parts well only in the lane it was tuned on (0.385 m to the right of
        # the base: scores fell from 0.40 to 0 as a shift's lane moved 0.2 m to the left, anchor run of 2026-11-25). So the
        # base shifts sideways until the part's lane is at that offset while it waits, stands still while the hand is on a
        # part, and returns home to reach the tote.
        Rb, pb = self._base(tr)
        if not hasattr(self, "base_home"): self.base_home = pb.copy(); self.base_yaw0 = math.atan2(Rb[1, 0], Rb[0, 0]); self.base_goal = pb[:2].copy()
        if self.state == "wait" and tr.get("phase") in ("staged", "live") and tr.get("pos") is not None:
            side = np.array([-math.sin(self.base_yaw0), math.cos(self.base_yaw0)])                # the base's own left
            shift = float((np.array(tr["pos"])[:2] - self.base_home[:2]) @ side) + PICK_SIDE
            self.base_goal = self.base_home[:2] + side * float(np.clip(shift, -0.25, 0.25))
        elif self.state in ("carry", "drop"): self.base_goal = self.base_home[:2].copy()
        if self.state not in ("follow", "lift"):
            e = Rb[:2, :2].T @ (self.base_goal - pb[:2]); yaw = math.atan2(Rb[1, 0], Rb[0, 0]) - self.base_yaw0
            row[SL["base"]] = [float(np.clip(4.0 * e[0], -0.5, 0.5)), float(np.clip(4.0 * e[1], -0.5, 0.5)), float(np.clip(-3.0 * yaw, -0.5, 0.5))]
        row[SL["arm_left"]] = self.home_left; row[SL["gl"]] = 1.0; row[SL["gr"]] = self.grip
        return row

    def _yaw_R(self, tr):
        """Gripper pointing straight down, opening axis along the base's y."""
        Rb, _ = self._base(tr); return Rb
