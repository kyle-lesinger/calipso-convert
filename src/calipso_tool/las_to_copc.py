import subprocess
import json
from pathlib import Path
from typing import Optional, Union
import tempfile


def las_to_copc(
    input_las: Union[str, Path],
    output_copc: Optional[Union[str, Path]] = None,
    pipeline_json: Optional[Union[str, Path]] = None
) -> Path:
    """
    Convert LAS file to Cloud-Optimized Point Cloud (COPC) format using PDAL.
    
    Parameters:
    -----------
    input_las : str or Path
        Path to input LAS file
    output_copc : str or Path, optional
        Path to output COPC file. If None, uses same name as input with .copc.laz extension
    pipeline_json : str or Path, optional
        Path to PDAL pipeline JSON file. If None, creates pipeline programmatically
    
    Returns:
    --------
    Path
        Path to the created COPC file
    """
    input_las = Path(input_las)
    
    # Generate output filename if not provided
    if output_copc is None:
        # Replace .las with .copc.laz
        output_copc = input_las.parent / f"{input_las.stem}.copc.laz"
    else:
        output_copc = Path(output_copc)
    
    # If pipeline JSON is provided, use it
    if pipeline_json is not None:
        pipeline_json = Path(pipeline_json)
        
        # Load and modify the pipeline
        with open(pipeline_json, 'r') as f:
            pipeline = json.load(f)
        
        # Update filenames in pipeline
        for stage in pipeline["pipeline"]:
            if stage["type"] == "readers.las":
                stage["filename"] = str(input_las)
            elif stage["type"] == "writers.copc":
                stage["filename"] = str(output_copc)
    else:
        # Create pipeline programmatically
        pipeline = {
            "pipeline": [
                {
                    "type": "readers.las",
                    "filename": str(input_las)
                },
                {
                    "type": "writers.copc",
                    "filename": str(output_copc)
                }
            ]
        }
    
    # Write temporary pipeline file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(pipeline, f, indent=2)
        temp_pipeline = f.name
    
    try:
        # Run PDAL pipeline
        print(f"Converting {input_las} to COPC format...")
        
        result = subprocess.run(
            ["pdal", "pipeline", temp_pipeline],
            capture_output=True,
            text=True,
            check=True
        )
        
        if result.returncode == 0:
            print(f"✓ Created: {output_copc}")
            
            # Get file info
            info_result = subprocess.run(
                ["pdal", "info", str(output_copc), "--summary"],
                capture_output=True,
                text=True,
                check=True
            )
            
            if info_result.returncode == 0:
                # Parse output size info
                import os
                input_size = os.path.getsize(input_las) / (1024 * 1024)  # MB
                output_size = os.path.getsize(output_copc) / (1024 * 1024)  # MB
                compression_ratio = (1 - output_size / input_size) * 100
                
                print(f"\nFile sizes:")
                print(f"  Input LAS: {input_size:.2f} MB")
                print(f"  Output COPC: {output_size:.2f} MB")
                print(f"  Compression: {compression_ratio:.1f}%")
        
        return output_copc
        
    except subprocess.CalledProcessError as e:
        print(f"✗ PDAL pipeline failed: {e}")
        print(f"Error output: {e.stderr}")
        raise
    
    finally:
        # Clean up temporary pipeline file
        Path(temp_pipeline).unlink(missing_ok=True)


def las_to_copc_pipeline(
    input_las: Union[str, Path],
    output_copc: Optional[Union[str, Path]] = None
) -> Path:
    """
    Convert LAS to COPC using the default pipeline JSON if available.
    
    This is a convenience wrapper that automatically finds the las2copc.json file.
    """
    input_las = Path(input_las)
    
    # Try to find pipeline JSON
    pipeline_json = Path(__file__).parent.parent / "pdal_pipeline" / "las2copc.json"
    
    if pipeline_json.exists():
        return las_to_copc(input_las, output_copc, pipeline_json)
    else:
        # Fall back to programmatic approach
        return las_to_copc(input_las, output_copc)


def batch_las_to_copc(
    directory: Union[str, Path],
    pattern: str = "*.las",
    skip_existing: bool = True
) -> tuple[list[Path], list[tuple[Path, str]]]:
    """
    Convert all LAS files in a directory to COPC format.
    
    Parameters:
    -----------
    directory : str or Path
        Directory containing LAS files
    pattern : str, default="*.las"
        Glob pattern for finding LAS files
    skip_existing : bool, default=True
        Skip conversion if COPC file already exists
    
    Returns:
    --------
    tuple[list[Path], list[tuple[Path, str]]]
        Lists of successful conversions and failed conversions with error messages
    """
    directory = Path(directory)
    las_files = list(directory.glob(pattern))
    
    print(f"Found {len(las_files)} LAS files to convert")
    
    successful = []
    failed = []
    
    for las_file in las_files:
        copc_file = las_file.parent / f"{las_file.stem}.copc.laz"
        
        if skip_existing and copc_file.exists():
            print(f"⏭️  Skipping {las_file.name} (COPC already exists)")
            successful.append(copc_file)
            continue
        
        try:
            result = las_to_copc_pipeline(las_file)
            successful.append(result)
        except Exception as e:
            failed.append((las_file, str(e)))
    
    print(f"\nBatch conversion complete:")
    print(f"  Successful: {len(successful)}")
    print(f"  Failed: {len(failed)}")
    
    return successful, failed


def main():
    """Command-line interface for LAS to COPC conversion."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Convert LAS file to COPC format")
    parser.add_argument("input_las", help="Path to input LAS file")
    parser.add_argument("-o", "--output", help="Path to output COPC file (optional)")
    parser.add_argument("-p", "--pipeline", help="Path to PDAL pipeline JSON file")
    parser.add_argument("--batch", action="store_true", 
                        help="Process all LAS files in the directory")
    parser.add_argument("--pattern", default="*.las",
                        help="Glob pattern for batch processing (default: *.las)")
    
    args = parser.parse_args()
    
    if args.batch:
        # Batch processing mode
        directory = Path(args.input_las).parent if Path(args.input_las).is_file() else Path(args.input_las)
        batch_las_to_copc(directory, args.pattern)
    else:
        # Single file mode
        if args.pipeline:
            las_to_copc(args.input_las, args.output, args.pipeline)
        else:
            las_to_copc_pipeline(args.input_las, args.output)


if __name__ == "__main__":
    main()