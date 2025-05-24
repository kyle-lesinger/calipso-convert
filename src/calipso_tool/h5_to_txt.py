import h5py
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Optional, Union


def h5_to_txt(
    input_h5: Union[str, Path],
    output_txt: Optional[Union[str, Path]] = None,
    variable_name: str = "var_to_grab",
    altitude_units: str = "km"
) -> Path:
    """
    Convert HDF5 file to space-delimited text file with 3D grid data.
    
    Parameters:
    -----------
    input_h5 : str or Path
        Path to input HDF5 file
    output_txt : str or Path, optional
        Path to output text file. If None, uses same name as input with .txt extension
    variable_name : str, default="var_to_grab"
        Name of the variable to extract from HDF5 file
    altitude_units : str, default="km"
        Units of altitude in the HDF5 file. If "km", will convert to meters.
    
    Returns:
    --------
    Path
        Path to the created text file
    """
    input_h5 = Path(input_h5)
    
    # Generate output filename if not provided
    if output_txt is None:
        output_txt = input_h5.with_suffix('.txt')
    else:
        output_txt = Path(output_txt)
    
    # Open HDF5 file and extract data
    with h5py.File(input_h5, "r") as f:
        # Extract coordinate arrays
        lat1d = f["Latitude_Midpoint"][0]    # shape (85,)
        lon1d = f["Longitude_Midpoint"][0]   # shape (72,)
        alt1d = f["Altitude_Midpoint"][0]    # shape (208,)
        
        # Extract the variable data
        if variable_name not in f:
            raise KeyError(f"Variable '{variable_name}' not found in HDF5 file. "
                         f"Available keys: {list(f.keys())}")
        
        var_data = f[variable_name][:]        # shape (85, 72, 208)
    
    # Create 3D coordinate grids
    latg, longg, altg = np.meshgrid(lat1d, lon1d, alt1d, indexing="ij")
    
    # Convert altitude to meters if needed
    if altitude_units.lower() == "km":
        altg = altg * 1000  # km to m
    
    # Flatten all arrays and create DataFrame
    df = pd.DataFrame({
        "X": longg.ravel(),                # lon → X
        "Y": latg.ravel(),                 # lat → Y
        "Z": altg.ravel(),                 # altitude
        variable_name: var_data.ravel().astype(np.float32),
    })
    
    # Save as space-delimited ASCII
    df.to_csv(output_txt, sep=" ", index=False, header=True)
    
    print(f"Converted {input_h5} to {output_txt}")
    print(f"Output contains {len(df)} points")
    
    return output_txt


def main():
    """Example usage of h5_to_txt function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Convert HDF5 file to text format")
    parser.add_argument("input_h5", help="Path to input HDF5 file")
    parser.add_argument("-o", "--output", help="Path to output text file (optional)")
    parser.add_argument("-v", "--variable", default="var_to_grab",
                        help="Name of variable to extract (default: var_to_grab)")
    parser.add_argument("--alt-units", default="km", choices=["km", "m"],
                        help="Altitude units in HDF5 file (default: km)")
    
    args = parser.parse_args()
    
    h5_to_txt(
        args.input_h5,
        args.output,
        args.variable,
        args.alt_units
    )


if __name__ == "__main__":
    main()