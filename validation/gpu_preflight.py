"""Fail closed unless Slurm, device access, CUDA and Vulkan select one GPU.

Author infrastructure check only; this is not part of the submitted task.
Run host mode in the allocation, then container mode before importing Isaac.
"""
import argparse
import ctypes as C
import glob
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET


def device_access():
    rows = []
    for name in sorted(glob.glob('/dev/nvidia[0-9]*')):
        try:
            fd = os.open(name, os.O_RDWR | os.O_CLOEXEC)
        except OSError as exc:
            rows.append(dict(path=name, allowed=False, errno=exc.errno))
        else:
            os.close(fd)
            rows.append(dict(path=name, allowed=True))
    return rows


def host():
    nodes = device_access()
    allowed = [row['path'] for row in nodes if row['allowed']]
    if len(allowed) != 1:
        raise RuntimeError(f'Expected exactly one accessible GPU device, got {nodes}')
    allocation = os.environ.get('SLURM_STEP_GPUS') or os.environ.get('SLURM_JOB_GPUS')
    if allocation != allowed[0].removeprefix('/dev/nvidia'):
        raise RuntimeError(f'Slurm allocation {allocation!r} does not match {allowed}')
    xml = ET.fromstring(subprocess.check_output(['nvidia-smi', '-q', '-x']))
    rows = [gpu for gpu in xml.findall('gpu')
            if '/dev/nvidia' + gpu.findtext('minor_number', '') == allowed[0]]
    if len(rows) != 1:
        raise RuntimeError('Cannot resolve allocated GPU minor to NVIDIA UUID')
    gpu = rows[0]
    uuid = gpu.findtext('uuid', '')
    if not uuid.startswith('GPU-'):
        raise RuntimeError(f'Unsupported GPU UUID: {uuid}')
    return dict(device_nodes=nodes, allocated_device=allowed[0], uuid=uuid,
                name=gpu.findtext('product_name'), pci_bus_id=gpu.findtext('pci/pci_bus_id'),
                driver_version=xml.findtext('driver_version'),
                slurm={k: v for k, v in os.environ.items()
                       if k.startswith('SLURM_') and ('GPU' in k or k == 'SLURM_JOB_ID')},
                cuda_visible_devices=os.environ.get('CUDA_VISIBLE_DEVICES'),
                cgroup=Path('/proc/self/cgroup').read_text())


def vulkan_devices():
    class Application(C.Structure):
        _fields_ = [('sType', C.c_uint32), ('pNext', C.c_void_p),
                    ('pApplicationName', C.c_char_p), ('applicationVersion', C.c_uint32),
                    ('pEngineName', C.c_char_p), ('engineVersion', C.c_uint32),
                    ('apiVersion', C.c_uint32)]

    class InstanceInfo(C.Structure):
        _fields_ = [('sType', C.c_uint32), ('pNext', C.c_void_p), ('flags', C.c_uint32),
                    ('application', C.POINTER(Application)), ('layerCount', C.c_uint32),
                    ('layers', C.c_void_p), ('extensionCount', C.c_uint32), ('extensions', C.c_void_p)]

    class DeviceID(C.Structure):
        _fields_ = [('sType', C.c_uint32), ('pNext', C.c_void_p),
                    ('deviceUUID', C.c_ubyte * 16), ('driverUUID', C.c_ubyte * 16),
                    ('deviceLUID', C.c_ubyte * 8), ('deviceNodeMask', C.c_uint32),
                    ('deviceLUIDValid', C.c_uint32)]

    class Properties(C.Structure):
        # Oversized, aligned storage for the core properties; only the fixed prefix is read.
        _fields_ = [('sType', C.c_uint32), ('pNext', C.c_void_p), ('data', C.c_uint64 * 512)]

    vk = C.CDLL('libvulkan.so.1')
    vk.vkCreateInstance.argtypes = [C.POINTER(InstanceInfo), C.c_void_p, C.POINTER(C.c_void_p)]
    vk.vkCreateInstance.restype = C.c_int32
    vk.vkEnumeratePhysicalDevices.argtypes = [C.c_void_p, C.POINTER(C.c_uint32), C.POINTER(C.c_void_p)]
    vk.vkEnumeratePhysicalDevices.restype = C.c_int32
    vk.vkGetPhysicalDeviceProperties2.argtypes = [C.c_void_p, C.POINTER(Properties)]
    vk.vkGetPhysicalDeviceProperties2.restype = None
    vk.vkDestroyInstance.argtypes = [C.c_void_p, C.c_void_p]
    vk.vkDestroyInstance.restype = None
    app = Application(sType=0, pApplicationName=b'allocation-check', apiVersion=(1 << 22) | (1 << 12))
    info = InstanceInfo(sType=1, application=C.pointer(app))
    instance = C.c_void_p()
    result = vk.vkCreateInstance(C.byref(info), None, C.byref(instance))
    if result != 0:
        raise RuntimeError(f'Vulkan instance creation failed: {result}')
    try:
        count = C.c_uint32()
        if vk.vkEnumeratePhysicalDevices(instance, C.byref(count), None) != 0 or count.value == 0:
            raise RuntimeError('No Vulkan devices')
        handles = (C.c_void_p * count.value)()
        if vk.vkEnumeratePhysicalDevices(instance, C.byref(count), handles) != 0:
            raise RuntimeError('Vulkan enumeration failed')
        rows = []
        for index, handle in enumerate(handles):
            ident = DeviceID(sType=1000071004)
            props = Properties(sType=1000059001, pNext=C.cast(C.pointer(ident), C.c_void_p))
            vk.vkGetPhysicalDeviceProperties2(handle, C.byref(props))
            data = bytes(props.data)
            rows.append(dict(index=index, uuid=bytes(ident.deviceUUID).hex(),
                             name=data[20:276].split(b'\0')[0].decode(),
                             vendor_id=int.from_bytes(data[8:12], 'little')))
        return rows
    finally:
        vk.vkDestroyInstance(instance, None)


def container(record):
    expected = json.loads(Path(record).read_text())
    nodes = device_access()
    if [r['path'] for r in nodes if r['allowed']] != [expected['allocated_device']]:
        raise RuntimeError(f'Container GPU device restriction differs: {nodes}')
    uuid = expected['uuid'][4:].replace('-', '').lower()
    devices = vulkan_devices()
    if len(devices) != 1 or devices[0]['uuid'] != uuid or devices[0]['vendor_id'] != 0x10DE:
        raise RuntimeError(f'Vulkan must expose only allocated NVIDIA UUID {uuid}: {devices}')
    import torch
    if torch.cuda.device_count() != 1:
        raise RuntimeError(f'CUDA sees {torch.cuda.device_count()} GPUs')
    cuda_uuid = str(torch.cuda.get_device_properties(0).uuid).lower().removeprefix('gpu-').replace('-', '')
    if cuda_uuid != uuid:
        raise RuntimeError(f'CUDA UUID {cuda_uuid} differs from allocated GPU {uuid}')
    return dict(device_nodes=nodes, vulkan=devices, cuda_uuid=cuda_uuid,
                active_gpu=0, single_allocated_gpu_verified=True,
                cgroup=Path('/proc/self/cgroup').read_text())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host-record')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    result = container(args.host_record) if args.host_record else host()
    Path(args.output).write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result), flush=True)
