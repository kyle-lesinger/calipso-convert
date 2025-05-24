from importlib import resources
import subprocess
from pathlib import Path
from typing import Optional, Union
from .h5_to_txt import h5_to_txt

def h4_to_h5(in_h4: Path, out_h5: Path):
    # locate the vendored binary
    bin_path = Path(resources.files("calipso_tool") / "bin" / "h4toh5convert")
    subprocess.run([str(bin_path), str(in_h4), str(out_h5)], check=True)
    return out_h5

def h4_to_txt(
    input_h4: Union[str, Path],
    output_txt: Optional[Union[str, Path]] = None,
    variable_name: str = "var_to_grab",
    altitude_units: str = "km",
    keep_h5: bool = True
) -> tuple[Path, Optional[Path]]:
    """
    Chain conversion from HDF4 to HDF5 to text format.
    
    Parameters:
    -----------
    input_h4 : str or Path
        Path to input HDF4 file
    output_txt : str or Path, optional
        Path to output text file. If None, uses same name as input with .txt extension
    variable_name : str, default="var_to_grab"
        Name of the variable to extract from HDF5 file
    altitude_units : str, default="km"
        Units of altitude in the HDF5 file. If "km", will convert to meters.
    keep_h5 : bool, default=True
        Whether to keep the intermediate HDF5 file
    
    Returns:
    --------
    tuple[Path, Optional[Path]]
        Paths to the created text file and HDF5 file (if kept)
    """
    input_h4 = Path(input_h4)
    
    # Generate intermediate HDF5 filename
    h5_file = input_h4.with_suffix('.h5')
    
    # Generate output text filename if not provided
    if output_txt is None:
        output_txt = input_h4.with_suffix('.txt')
    else:
        output_txt = Path(output_txt)
    
    print(f"Step 1: Converting HDF4 to HDF5...")
    try:
        h4_to_h5(input_h4, h5_file)
        print(f"  ✓ Created: {h5_file}")
    except Exception as e:
        print(f"  ✗ HDF4 to HDF5 conversion failed: {e}")
        raise
    
    print(f"\nStep 2: Converting HDF5 to text...")
    try:
        h5_to_txt(h5_file, output_txt, variable_name, altitude_units)
        print(f"  ✓ Created: {output_txt}")
    except Exception as e:
        print(f"  ✗ HDF5 to text conversion failed: {e}")
        # Clean up HDF5 file if conversion failed
        if h5_file.exists() and not keep_h5:
            h5_file.unlink()
        raise
    
    # Remove intermediate HDF5 file if requested
    if not keep_h5 and h5_file.exists():
        h5_file.unlink()
        print(f"\n  Removed intermediate file: {h5_file}")
        return output_txt, None
    
    return output_txt, h5_file

__all__ = ['h4_to_h5', 'h5_to_txt', 'h4_to_txt']