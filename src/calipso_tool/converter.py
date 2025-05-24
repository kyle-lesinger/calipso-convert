from importlib import resources
import subprocess
from pathlib import Path

def h4_to_h5(in_h4: Path, out_h5: Path):
    # locate the vendored binary
    bin_path = Path(resources.files("calipso_tool") / "bin" / "h4toh5convert")
    subprocess.run([str(bin_path), str(in_h4), str(out_h5)], check=True)
    return out_h5