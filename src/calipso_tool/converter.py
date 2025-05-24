import subprocess
from pathlib import Path

def h4_to_h5(in_h4: Path, out_h5: Path):
    """
    Calls the binary `h4toh5convert` on in_h4, writes to out_h5.
    """
    cmd = ["h4toh5convert", str(in_h4), str(out_h5)]
    subprocess.run(cmd, check=True)
    return out_h5

