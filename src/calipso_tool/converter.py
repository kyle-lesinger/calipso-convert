from importlib import resources
import subprocess
import logging # Added for potential direct use, though 'from .' is preferred
from pathlib import Path
from typing import Optional, Union
# Import the package-level logger
from . import logger
from .h5_to_txt import h5_to_txt
from .txt_to_las import txt_to_las, txt_to_las_with_json
from .las_to_copc import las_to_copc_pipeline

def h4_to_h5(in_h4: Path, out_h5: Path):
    # locate the vendored binary
    bin_path = Path(resources.files("calipso_tool") / "bin" / "h4toh5convert")
    subprocess.run([str(bin_path), str(in_h4), str(out_h5)], check=True)
    return out_h5

def h4_to_txt(
    input_h4: Union[str, Path],
    output_txt: Optional[Union[str, Path]] = None,
    variable_name: str = "Extinction_Coefficient_532",
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

    logger.info("Step 1: Converting HDF4 to HDF5...")
    try:
        h4_to_h5(input_h4, h5_file)
        logger.info("  ✓ Created: %s", h5_file)
    except Exception as e:
        logger.error("  ✗ HDF4 to HDF5 conversion failed: %s", e, exc_info=True)
        raise

    logger.info("Step 2: Converting HDF5 to text...")
    try:
        h5_to_txt(h5_file, output_txt, variable_name, altitude_units)
        logger.info("  ✓ Created: %s", output_txt)
    except Exception as e:
        logger.error("  ✗ HDF5 to text conversion failed: %s", e, exc_info=True)
        # Clean up HDF5 file if conversion failed
        if h5_file.exists() and not keep_h5:
            h5_file.unlink()
        raise

    # Remove intermediate HDF5 file if requested
    if not keep_h5 and h5_file.exists():
        h5_file.unlink()
        logger.info("  Removed intermediate file: %s", h5_file)
        return output_txt, None

    return output_txt, h5_file

def txt_to_las_pipeline(
    input_txt: Union[str, Path],
    output_las: Optional[Union[str, Path]] = None,
    variable_name: str = "Extinction_Coefficient_532",
    pipeline_json: Optional[Union[str, Path]] = None
) -> Path:
    """
    Convert text file to LAS format using PDAL pipeline.
    
    This is a convenience wrapper that automatically finds the pipeline JSON.
    """
    input_txt = Path(input_txt)
    
    if output_las is None:
        output_las = input_txt.with_suffix('.las')
    else: # Ensure output_las is a Path object
        output_las = Path(output_las)

    # Try to find pipeline JSON if not provided
    if pipeline_json is None:
        try:
            # Use importlib.resources to access package data
            pipeline_json_path = resources.files("calipso_tool.pdal_pipelines").joinpath("h5tolas.json")
            if pipeline_json_path.exists(): # Check if the resource exists
                logger.info("Using PDAL pipeline from package resources: %s", pipeline_json_path)
                # As per instruction, passing str(pipeline_json_path).
                # Note: txt_to_las_with_json needs to correctly handle this path,
                # which might require resources.as_file() in its implementation if this is still a Traversable.
                return txt_to_las_with_json(input_txt, output_las, variable_name, str(pipeline_json_path))
            else:
                logger.warning("PDAL pipeline JSON 'h5tolas.json' not found at %s. Falling back to programmatic LAS creation.", pipeline_json_path)
                pass # Fall through to programmatic approach
        except Exception as e: # Catch potential errors with resource loading
            logger.warning("Could not load PDAL pipeline JSON: %s. Falling back to programmatic LAS creation.", e, exc_info=True)
            pass # Fall through to programmatic approach
            
    elif isinstance(pipeline_json, (str, Path)) and Path(pipeline_json).exists(): # If user provided a valid path
        logger.info("Using user-provided PDAL pipeline: %s", pipeline_json)
        return txt_to_las_with_json(input_txt, output_las, variable_name, pipeline_json)
    else: # User provided a path, but it doesn't exist, or pipeline_json is invalid type
        if isinstance(pipeline_json, (str,Path)): # only log not found if it was a path
             logger.warning("User-provided PDAL pipeline not found: %s. Falling back to programmatic LAS creation.", pipeline_json)
        else: # log invalid type if it wasn't a path
             logger.warning("Invalid PDAL pipeline JSON value specified: %s. Falling back to programmatic LAS creation.", pipeline_json)
        pass # Fall through to programmatic approach

    # Fall back to programmatic approach if JSON pipeline is not found or specified
    logger.info("No valid PDAL JSON pipeline specified or found, using programmatic LAS creation for %s.", input_txt)
    return txt_to_las(input_txt, output_las, variable_name)


def h4_to_las(
    input_h4: Union[str, Path],
    output_las: Optional[Union[str, Path]] = None,
    variable_name: str = "Extinction_Coefficient_532",
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
        logger.info("Step 1: Converting HDF4 to HDF5...")
        h4_to_h5(input_h4, h5_file)
        logger.info("  ✓ Created: %s", h5_file)

        # Step 2: HDF5 to Text
        logger.info("Step 2: Converting HDF5 to text...")
        h5_to_txt(h5_file, txt_file, variable_name, altitude_units)
        logger.info("  ✓ Created: %s", txt_file)

        # Step 3: Text to LAS
        logger.info("Step 3: Converting text to LAS...")
        txt_to_las_pipeline(txt_file, output_las, variable_name)
        logger.info("  ✓ Created: %s", output_las)

    except Exception as e:
        logger.error("✗ Pipeline failed during HDF4->LAS: %s", e, exc_info=True)
        # Clean up any intermediate files on failure
        if not keep_intermediates:
            for f in [h5_file, txt_file]:
                if f.exists():
                    f.unlink()
        raise

    # Clean up intermediate files if requested
    if not keep_intermediates:
        cleaned_files_log = []
        if h5_file and h5_file.exists(): # Ensure h5_file is not None before checking exists
            h5_file.unlink()
            cleaned_files_log.append(str(h5_file))
            h5_file = None
        if txt_file and txt_file.exists(): # Ensure txt_file is not None before checking exists
            txt_file.unlink()
            cleaned_files_log.append(str(txt_file))
            txt_file = None
        if cleaned_files_log:
            logger.info("Cleaned up intermediate files: %s", ', '.join(cleaned_files_log))

    return output_las, h5_file, txt_file


def h4_to_copc(
    input_h4: Union[str, Path],
    output_copc: Optional[Union[str, Path]] = None,
    variable_name: str = "Extinction_Coefficient_532",
    altitude_units: str = "km",
    keep_intermediates: bool = False
) -> tuple[Path, Optional[Path], Optional[Path], Optional[Path], Optional[Path]]:
    """
    Complete pipeline: HDF4 → HDF5 → Text → LAS → COPC
    
    Parameters:
    -----------
    input_h4 : str or Path
        Path to input HDF4 file
    output_copc : str or Path, optional
        Path to output COPC file. If None, uses same name as input with .copc.laz extension
    variable_name : str, default="var_to_grab"
        Name of the variable to extract from HDF5 file
    altitude_units : str, default="km"
        Units of altitude in the HDF5 file. If "km", will convert to meters.
    keep_intermediates : bool, default=False
        Whether to keep intermediate files (HDF5, text, LAS)
    
    Returns:
    --------
    tuple[Path, Optional[Path], Optional[Path], Optional[Path], Optional[Path]]
        Paths to COPC file, HDF5 file (if kept), text file (if kept), LAS file (if kept)
    """
    input_h4 = Path(input_h4)
    
    # Generate intermediate filenames
    h5_file = input_h4.with_suffix('.h5')
    txt_file = input_h4.with_suffix('.txt')
    las_file = input_h4.with_suffix('.las')
    
    if output_copc is None:
        output_copc = input_h4.parent / f"{input_h4.stem}.copc.laz"
    else:
        output_copc = Path(output_copc)
    
    try:
        # Step 1-3: HDF4 → HDF5 → Text → LAS
        logger.info("Running HDF4 → LAS sub-pipeline...")
        # Pass original keep_intermediates, h4_to_las will manage its own logging for cleanup
        las_result, h5_kept, txt_kept = h4_to_las(
            input_h4,
            las_file,
            variable_name,
            altitude_units,
            keep_intermediates=keep_intermediates # Pass the main flag
        )
        # If h4_to_las was set to clean up, h5_kept and txt_kept would be None
        # If it was set to keep, they will be paths.

        # Step 4: LAS → COPC
        logger.info("Step 4: Converting LAS to COPC...")
        las_to_copc_pipeline(las_result, output_copc) # las_result is the output_las from h4_to_las
        logger.info("  ✓ Created: %s", output_copc)

        logger.info("="*50)
        logger.info("Pipeline complete! Final output: %s", output_copc)
        logger.info("="*50)

    except Exception as e:
        logger.error("✗ Pipeline failed during HDF4->COPC: %s", e, exc_info=True)
        # Intermediate files are handled by h4_to_las if keep_intermediates is False.
        # If keep_intermediates is True, they are kept.
        # The main concern here is if las_file was created before this specific step failed.
        if not keep_intermediates:
            # This check is a bit redundant if h4_to_las already cleaned,
            # but good for safety if error happens between h4_to_las and las_to_copc
            if las_file.exists(): # las_file is the *intended* path for LAS
                las_file.unlink()
                logger.info("Cleaned up intermediate LAS file: %s", las_file)
        raise

    if not keep_intermediates:
        # h4_to_las would have cleaned H5 and TXT if keep_intermediates was false.
        # We only need to worry about the LAS file if it still exists.
        if las_file.exists(): # las_file is the *intended* path
             las_file.unlink()
             logger.info("Cleaned up intermediate LAS file: %s", las_file)
        return output_copc, None, None, None # Return None for all intermediate files
    else:
        # If intermediates are kept, h5_kept and txt_kept come from h4_to_las.
        # las_file path is the one used for conversion.
        return output_copc, h5_kept, txt_kept, (las_file if las_file.exists() else None)


__all__ = [
    'h4_to_h5', 
    'h5_to_txt', 
    'h4_to_txt', 
    'txt_to_las', 
    'txt_to_las_pipeline', 
    'h4_to_las',
    'las_to_copc_pipeline',
    'h4_to_copc'
]