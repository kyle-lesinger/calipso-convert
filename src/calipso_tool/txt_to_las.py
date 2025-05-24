import subprocess
import json
from pathlib import Path
from typing import Optional, Union
import tempfile


def txt_to_las(
    input_txt: Union[str, Path],
    output_las: Optional[Union[str, Path]] = None,
    variable_name: str = "var_to_grab",
    scale_x: float = 1e-5,
    scale_y: float = 1e-5,
    scale_z: float = 0.01,
    srs: str = "EPSG:4326"
) -> Path:
    """
    Convert text file to LAS format using PDAL pipeline.
    
    Parameters:
    -----------
    input_txt : str or Path
        Path to input text file
    output_las : str or Path, optional
        Path to output LAS file. If None, uses same name as input with .las extension
    variable_name : str, default="var_to_grab"
        Name of the variable that was extracted (will be added as extra dimension)
    scale_x, scale_y, scale_z : float
        Scale factors for X, Y, Z coordinates
    srs : str, default="EPSG:4326"
        Spatial reference system
    
    Returns:
    --------
    Path
        Path to the created LAS file
    """
    input_txt = Path(input_txt)
    
    # Generate output filename if not provided
    if output_las is None:
        output_las = input_txt.with_suffix('.las')
    else:
        output_las = Path(output_las)
    
    # Create custom pipeline with dynamic variable name
    pipeline = {
        "pipeline": [
            {
                "type": "readers.text",
                "filename": str(input_txt),
                "separator": " ",
                "default_srs": srs
            },
            {
                "type": "writers.las",
                "filename": str(output_las),
                "scale_x": scale_x,
                "scale_y": scale_y,
                "scale_z": scale_z,
                "offset_x": 0.0,
                "offset_y": 0.0,
                "offset_z": 0.0,
                "extra_dims": [
                    f"{variable_name}=float"
                ]
            }
        ]
    }
    
    # Write temporary pipeline file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(pipeline, f, indent=2)
        temp_pipeline = f.name
    
    try:
        # Run PDAL pipeline
        print(f"Converting {input_txt} to LAS format...")
        print(f"Extra dimension: {variable_name}")
        
        result = subprocess.run(
            ["pdal", "pipeline", temp_pipeline],
            capture_output=True,
            text=True,
            check=True
        )
        
        if result.returncode == 0:
            print(f"✓ Created: {output_las}")
            
            # Get file info
            info_result = subprocess.run(
                ["pdal", "info", str(output_las), "--summary"],
                capture_output=True,
                text=True,
                check=True
            )
            
            if info_result.returncode == 0:
                print(f"LAS file info:")
                print(info_result.stdout)
        
        return output_las
        
    except subprocess.CalledProcessError as e:
        print(f"✗ PDAL pipeline failed: {e}")
        print(f"Error output: {e.stderr}")
        raise
    
    finally:
        # Clean up temporary pipeline file
        Path(temp_pipeline).unlink(missing_ok=True)


def txt_to_las_with_json(
    input_txt: Union[str, Path],
    output_las: Optional[Union[str, Path]] = None,
    variable_name: str = "var_to_grab",
    pipeline_json: Optional[Union[str, Path]] = None
) -> Path:
    """
    Convert text file to LAS format using existing PDAL pipeline JSON file.
    
    This function modifies the pipeline JSON to use the correct input/output files
    and variable name.
    
    Parameters:
    -----------
    input_txt : str or Path
        Path to input text file
    output_las : str or Path, optional
        Path to output LAS file. If None, uses same name as input with .las extension
    variable_name : str, default="var_to_grab"
        Name of the variable that was extracted (will be added as extra dimension)
    pipeline_json : str or Path, optional
        Path to pipeline JSON file. If None, uses default h5tolas.json
    
    Returns:
    --------
    Path
        Path to the created LAS file
    """
    input_txt = Path(input_txt)
    
    # Generate output filename if not provided
    if output_las is None:
        output_las = input_txt.with_suffix('.las')
    else:
        output_las = Path(output_las)
    
    # Find pipeline JSON if not provided
    if pipeline_json is None:
        # Look for h5tolas.json in various locations
        possible_paths = [
            Path("h5tolas.json"),
            Path("src/pdal_pipeline/h5tolas.json"),
            Path(__file__).parent.parent / "pdal_pipeline" / "h5tolas.json"
        ]
        
        for path in possible_paths:
            if path.exists():
                pipeline_json = path
                break
        else:
            # If not found, use the programmatic approach
            return txt_to_las(input_txt, output_las, variable_name)
    
    pipeline_json = Path(pipeline_json)
    
    # Load and modify the pipeline
    with open(pipeline_json, 'r') as f:
        pipeline = json.load(f)
    
    # Update the pipeline with actual values
    for stage in pipeline["pipeline"]:
        if stage["type"] == "readers.text":
            stage["filename"] = str(input_txt)
        elif stage["type"] == "writers.las":
            stage["filename"] = str(output_las)
            # Update extra_dims with the actual variable name
            stage["extra_dims"] = [f"{variable_name}=float"]
    
    # Write temporary modified pipeline
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(pipeline, f, indent=2)
        temp_pipeline = f.name
    
    try:
        # Run PDAL pipeline
        print(f"Converting {input_txt} to LAS format using {pipeline_json.name}...")
        print(f"Extra dimension: {variable_name}")
        
        result = subprocess.run(
            ["pdal", "pipeline", temp_pipeline],
            capture_output=True,
            text=True,
            check=True
        )
        
        if result.returncode == 0:
            print(f"✓ Created: {output_las}")
        
        return output_las
        
    except subprocess.CalledProcessError as e:
        print(f"✗ PDAL pipeline failed: {e}")
        print(f"Error output: {e.stderr}")
        raise
    
    finally:
        # Clean up temporary pipeline file
        Path(temp_pipeline).unlink(missing_ok=True)


def main():
    """Command-line interface for txt_to_las conversion."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Convert text file to LAS format using PDAL")
    parser.add_argument("input_txt", help="Path to input text file")
    parser.add_argument("-o", "--output", help="Path to output LAS file (optional)")
    parser.add_argument("-v", "--variable", default="var_to_grab",
                        help="Name of variable (default: var_to_grab)")
    parser.add_argument("-p", "--pipeline", help="Path to PDAL pipeline JSON file")
    parser.add_argument("--scale-x", type=float, default=1e-5,
                        help="Scale factor for X coordinate (default: 1e-5)")
    parser.add_argument("--scale-y", type=float, default=1e-5,
                        help="Scale factor for Y coordinate (default: 1e-5)")
    parser.add_argument("--scale-z", type=float, default=0.01,
                        help="Scale factor for Z coordinate (default: 0.01)")
    parser.add_argument("--srs", default="EPSG:4326",
                        help="Spatial reference system (default: EPSG:4326)")
    
    args = parser.parse_args()
    
    if args.pipeline:
        txt_to_las_with_json(
            args.input_txt,
            args.output,
            args.variable,
            args.pipeline
        )
    else:
        txt_to_las(
            args.input_txt,
            args.output,
            args.variable,
            args.scale_x,
            args.scale_y,
            args.scale_z,
            args.srs
        )


if __name__ == "__main__":
    main()