from importlib import resources
import subprocess
from pathlib import Path
from typing import Optional, Union
from .h5_to_txt import h5_to_txt
from .txt_to_las import txt_to_las, txt_to_las_with_json

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

def txt_to_las_pipeline(
    input_txt: Union[str, Path],
    output_las: Optional[Union[str, Path]] = None,
    variable_name: str = "var_to_grab",
    pipeline_json: Optional[Union[str, Path]] = None
) -> Path:
    """
    Convert text file to LAS format using PDAL pipeline.
    
    This is a convenience wrapper that automatically finds the pipeline JSON.
    """
    input_txt = Path(input_txt)
    
    if output_las is None:
        output_las = input_txt.with_suffix('.las')
    
    # Try to find pipeline JSON if not provided
    if pipeline_json is None:
        # Look for h5tolas.json relative to this file
        pipeline_json = Path(__file__).parent.parent / "pdal_pipeline" / "h5tolas.json"
        if pipeline_json.exists():
            return txt_to_las_with_json(input_txt, output_las, variable_name, pipeline_json)
    
    # Fall back to programmatic approach
    return txt_to_las(input_txt, output_las, variable_name)


def h4_to_las(
    input_h4: Union[str, Path],
    output_las: Optional[Union[str, Path]] = None,
    variable_name: str = "var_to_grab",
    altitude_units: str = "km",
    keep_intermediates: bool = False
) -> tuple[Path, Optional[Path], Optional[Path]]:
    """
    Complete pipeline: HDF4 → HDF5 → Text → LAS
    
    Parameters:
    -----------
    input_h4 : str or Path
        Path to input HDF4 file
    output_las : str or Path, optional
        Path to output LAS file. If None, uses same name as input with .las extension
    variable_name : str, default="var_to_grab"
        Name of the variable to extract from HDF5 file
    altitude_units : str, default="km"
        Units of altitude in the HDF5 file. If "km", will convert to meters.
    keep_intermediates : bool, default=False
        Whether to keep intermediate HDF5 and text files
    
    Returns:
    --------
    tuple[Path, Optional[Path], Optional[Path]]
        Paths to LAS file, HDF5 file (if kept), and text file (if kept)
    """
    input_h4 = Path(input_h4)
    
    # Generate intermediate filenames
    h5_file = input_h4.with_suffix('.h5')
    txt_file = input_h4.with_suffix('.txt')
    
    if output_las is None:
        output_las = input_h4.with_suffix('.las')
    else:
        output_las = Path(output_las)
    
    try:
        # Step 1: HDF4 to HDF5
        print("Step 1: Converting HDF4 to HDF5...")
        h4_to_h5(input_h4, h5_file)
        print(f"  ✓ Created: {h5_file}")
        
        # Step 2: HDF5 to Text
        print(f"\\nStep 2: Converting HDF5 to text...")
        h5_to_txt(h5_file, txt_file, variable_name, altitude_units)
        print(f"  ✓ Created: {txt_file}")
        
        # Step 3: Text to LAS
        print(f"\\nStep 3: Converting text to LAS...")
        txt_to_las_pipeline(txt_file, output_las, variable_name)
        print(f"  ✓ Created: {output_las}")
        
    except Exception as e:
        print(f"\\n✗ Pipeline failed: {e}")
        # Clean up any intermediate files on failure
        if not keep_intermediates:
            for f in [h5_file, txt_file]:
                if f.exists():
                    f.unlink()
        raise
    
    # Clean up intermediate files if requested
    if not keep_intermediates:
        files_to_remove = []
        if h5_file.exists():
            h5_file.unlink()
            files_to_remove.append(h5_file)
            h5_file = None
        if txt_file.exists():
            txt_file.unlink()
            files_to_remove.append(txt_file)
            txt_file = None
        if files_to_remove:
            print(f"\\nCleaned up intermediate files: {', '.join(str(f) for f in files_to_remove)}")
    
    return output_las, h5_file, txt_file


__all__ = ['h4_to_h5', 'h5_to_txt', 'h4_to_txt', 'txt_to_las', 'txt_to_las_pipeline', 'h4_to_las']