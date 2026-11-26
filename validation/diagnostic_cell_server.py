"""Author-only factory traceback logging; all protocol/physics stay in task code."""
import sys
import traceback

sys.path.insert(0, '/task/tests')
from cell_server import serve

def make_cell(station, seed, parts, salt=0, assisted=False):
    try:
        import cell_env
        return cell_env.Cell(station, seed, n_parts=parts, salt=salt, assisted=assisted)
    except Exception:
        traceback.print_exc()
        raise

serve(make_cell)
try:
    import omnigibson as og
    og.shutdown()
except Exception:
    pass
