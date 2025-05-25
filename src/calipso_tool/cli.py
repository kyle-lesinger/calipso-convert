import sys
from pathlib import Path
import click
# Import the package-level logger
from . import logger 
from .converter import h4_to_h5, h4_to_copc

# You can create a command group
@click.group()
def cli():
    """CALIPSO Conversion Toolkit CLI"""
    pass

@cli.command("h4toh5")
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.option("--output-file", type=click.Path(dir_okay=False, resolve_path=True), default=None, help="Optional output HDF5 filename.")
def h4toh5_command(input_file, output_file):
    """Converts a CALIPSO HDF4 file to HDF5 format."""
    in_path = Path(input_file)
    if output_file:
        out_path = Path(output_file)
    else:
        out_path = in_path.with_suffix(".h5")
    
    logger.info("Converting %s → %s…", in_path, out_path)
    try:
        h4_to_h5(in_path, out_path)
        logger.info("✓ Conversion successful: %s", out_path)
    except Exception as e:
        logger.error("✗ Error during HDF4 to HDF5 conversion: %s", e, exc_info=True)
        sys.exit(1)

@cli.command("convert")
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.option("--output-file", type=click.Path(dir_okay=False, resolve_path=True), default=None, help="Optional output COPC filename (e.g., output.copc.laz).")
@click.option("-v", "--variable", "variable_name", default="Extinction_Coefficient_532", show_default=True, help="Variable name to extract.")
@click.option("-k", "--keep-intermediates", is_flag=True, help="Keep intermediate files (HDF5, TXT, LAS).")
def convert_full_pipeline_command(input_file, output_file, variable_name, keep_intermediates):
    """Runs the full CALIPSO HDF4 to COPC conversion pipeline."""
    in_path = Path(input_file)
    
    if output_file:
        out_copc_path = Path(output_file)
    else:
        out_copc_path = in_path.parent / f"{in_path.stem}.copc.laz"

    logger.info("Starting full conversion for %s...", in_path)
    logger.info("  Output COPC: %s", out_copc_path)
    logger.info("  Variable: %s", variable_name)
    logger.info("  Keep intermediates: %s", keep_intermediates)

    try:
        # Assuming h4_to_copc returns: copc_file, h5_file, txt_file, las_file
        # The actual return tuple might vary based on previous readings, adjust if necessary.
        # Based on converter.py, it's:
        # output_copc, h5_file, txt_file, las_file (if keep_intermediates is True)
        # or output_copc, None, None, None (if keep_intermediates is False)
        
        copc_result, h5_kept, txt_kept, las_kept = h4_to_copc(
            input_h4=in_path,
            output_copc=out_copc_path,
            variable_name=variable_name,
            altitude_units="km", # Assuming default, or make this an option
            keep_intermediates=keep_intermediates
        )
        logger.info("✓ Full pipeline successful: %s", copc_result)
        if keep_intermediates:
            if h5_kept:
                logger.info("  Intermediate HDF5 kept: %s", h5_kept)
            if txt_kept:
                logger.info("  Intermediate TXT kept: %s", txt_kept)
            if las_kept:
                logger.info("  Intermediate LAS kept: %s", las_kept)
    except Exception as e:
        logger.error("✗ Error during full pipeline conversion: %s", e, exc_info=True)
        # Consider more specific error handling or logging here
        sys.exit(1)

# Entry point for the CLI application
# This replaces the old main function if it was the direct entry point.
# If you have `if __name__ == "__main__":` block, update it to call `cli()`.
# For setuptools entry points, `cli` group is usually the target.

# Example of how you might make it runnable directly (though usually handled by setup.py/pyproject.toml entry points)
# if __name__ == '__main__':
#    cli()
