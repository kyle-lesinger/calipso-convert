# CALIPSO Tool Documentation

## Overview
This package provides a complete pipeline for converting CALIPSO atmospheric data from HDF4 format to Cloud-Optimized Point Cloud (COPC) format, with intermediate steps for HDF5, text, and LAS formats.

## Complete Pipeline
```
HDF4 → HDF5 → Text (ASCII) → LAS → COPC
```

## Module Structure

### `__init__.py`
Module initialization file that imports main functions.

### `cli.py`
Command-line interface for the CALIPSO conversion tool.

#### Functions

##### `main(input_file)`
Entry point for the CLI application.

**Parameters:**
- `input_file` (Click Path): Path to the input HDF4 file
  - Must exist
  - Cannot be a directory
  - Required argument

**Returns:** None (exits with sys.exit(0))

**Example:**
```bash
cali-convert /path/to/input.hdf
# Output: /path/to/input.h5
```

### `converter.py`
Core module that orchestrates all conversion pipelines.

#### Functions

##### `h4_to_h5(in_h4: Path, out_h5: Path) -> Path`
Converts HDF4 files to HDF5 format using a vendored binary converter.

**Parameters:**
- `in_h4` (Path): Path to the input HDF4 file
- `out_h5` (Path): Path where the output HDF5 file will be saved

**Returns:** Path to the created HDF5 file

##### `h4_to_txt(input_h4, output_txt=None, variable_name="var_to_grab", altitude_units="km", keep_h5=True) -> tuple[Path, Optional[Path]]`
Chains HDF4 to HDF5 to text conversion.

**Parameters:**
- `input_h4`: Path to input HDF4 file
- `output_txt`: Optional output text file path (defaults to same name with .txt)
- `variable_name`: Name of the variable to extract from HDF5
- `altitude_units`: Units of altitude ("km" or "m")
- `keep_h5`: Whether to keep intermediate HDF5 file

**Returns:** Tuple of (text file path, HDF5 file path if kept)

##### `txt_to_las_pipeline(input_txt, output_las=None, variable_name="var_to_grab", pipeline_json=None) -> Path`
Converts text file to LAS format using PDAL pipeline.

**Parameters:**
- `input_txt`: Path to input text file
- `output_las`: Optional output LAS file path
- `variable_name`: Variable name to include as extra dimension
- `pipeline_json`: Optional path to custom PDAL pipeline JSON

**Returns:** Path to created LAS file

##### `h4_to_las(input_h4, output_las=None, variable_name="var_to_grab", altitude_units="km", keep_intermediates=False) -> tuple[Path, Optional[Path], Optional[Path]]`
Complete pipeline from HDF4 to LAS format.

**Parameters:**
- `input_h4`: Path to input HDF4 file
- `output_las`: Optional output LAS file path
- `variable_name`: Variable to extract from HDF5
- `altitude_units`: Units of altitude in HDF5
- `keep_intermediates`: Whether to keep HDF5 and text files

**Returns:** Tuple of (LAS file, HDF5 file if kept, text file if kept)

##### `h4_to_copc(input_h4, output_copc=None, variable_name="var_to_grab", altitude_units="km", keep_intermediates=False) -> tuple[Path, Optional[Path], Optional[Path], Optional[Path]]`
Complete pipeline from HDF4 to COPC format.

**Parameters:**
- `input_h4`: Path to input HDF4 file
- `output_copc`: Optional output COPC file path (defaults to .copc.laz)
- `variable_name`: Variable to extract from HDF5
- `altitude_units`: Units of altitude in HDF5
- `keep_intermediates`: Whether to keep intermediate files

**Returns:** Tuple of (COPC file, HDF5 file if kept, text file if kept, LAS file if kept)

**Example:**
```python
from calipso_tool.converter import h4_to_copc

copc_file, _, _, _ = h4_to_copc(
    "input.hdf",
    variable_name="Extinction_Coefficient_532",
    keep_intermediates=False
)
```

### `h5_to_txt.py`
Converts HDF5 files to space-delimited text format with 3D grid data.

#### Functions

##### `h5_to_txt(input_h5, output_txt=None, variable_name="var_to_grab", altitude_units="km") -> Path`
Extracts 3D grid data from HDF5 and saves as text.

**Parameters:**
- `input_h5`: Path to input HDF5 file
- `output_txt`: Optional output text file path
- `variable_name`: Name of the 3D variable to extract
- `altitude_units`: Units of altitude ("km" converts to meters)

**Returns:** Path to created text file

**Required HDF5 Structure:**
- `Latitude_Midpoint[0]` - 1D array of latitudes
- `Longitude_Midpoint[0]` - 1D array of longitudes
- `Altitude_Midpoint[0]` - 1D array of altitudes
- Selected variable with shape matching grid dimensions

**Output Format:**
Space-delimited text file with columns: X (lon), Y (lat), Z (alt), variable_name

### `txt_to_las.py`
Converts text point cloud data to LAS format using PDAL.

#### Functions

##### `txt_to_las(input_txt, output_las=None, variable_name="var_to_grab", scale_x=1e-5, scale_y=1e-5, scale_z=0.01, srs="EPSG:4326") -> Path`
Programmatic conversion from text to LAS with customizable parameters.

**Parameters:**
- `input_txt`: Path to input text file
- `output_las`: Optional output LAS file path
- `variable_name`: Variable name for extra dimension
- `scale_x/y/z`: Scale factors for coordinates
- `srs`: Spatial reference system

**Returns:** Path to created LAS file

##### `txt_to_las_with_json(input_txt, output_las=None, variable_name="var_to_grab", pipeline_json=None) -> Path`
Converts text to LAS using existing PDAL pipeline JSON file.

**Parameters:**
- `input_txt`: Path to input text file
- `output_las`: Optional output LAS file path
- `variable_name`: Variable name for extra dimension
- `pipeline_json`: Path to PDAL pipeline JSON

**Returns:** Path to created LAS file

### `las_to_copc.py`
Converts LAS files to Cloud-Optimized Point Cloud (COPC) format.

#### Functions

##### `las_to_copc(input_las, output_copc=None, pipeline_json=None) -> Path`
Converts LAS to COPC format using PDAL.

**Parameters:**
- `input_las`: Path to input LAS file
- `output_copc`: Optional output COPC file path (defaults to .copc.laz)
- `pipeline_json`: Optional path to custom pipeline JSON

**Returns:** Path to created COPC file

##### `las_to_copc_pipeline(input_las, output_copc=None) -> Path`
Convenience wrapper that automatically finds the las2copc.json pipeline.

##### `batch_las_to_copc(directory, pattern="*.las", skip_existing=True) -> tuple[list[Path], list[tuple[Path, str]]]`
Batch converts all LAS files in a directory to COPC format.

**Parameters:**
- `directory`: Directory containing LAS files
- `pattern`: Glob pattern for finding LAS files
- `skip_existing`: Skip if COPC already exists

**Returns:** Tuple of (successful conversions, failed conversions with errors)

## Pipeline JSON Files

### `src/pdal_pipeline/h5tolas.json`
PDAL pipeline for converting text to LAS format:
- Reads space-delimited text
- Applies coordinate scaling
- Adds extra dimensions for variables
- Outputs LAS format

### `src/pdal_pipeline/las2copc.json`
PDAL pipeline for converting LAS to COPC format:
- Reads LAS files
- Applies LAZ compression
- Creates hierarchical structure
- Outputs COPC format

## Binary Dependencies

### `bin/h4toh5convert`
Vendored binary tool that performs HDF4 to HDF5 conversion. This binary is included with the package and is automatically located by the converter module.

## Command-Line Usage

### Basic HDF4 to HDF5 conversion:
```bash
cali-convert input.hdf
```

### Module-specific CLI usage:
```bash
# HDF5 to text
python -m calipso_tool.h5_to_txt input.h5 -v Extinction_Coefficient_532

# Text to LAS
python -m calipso_tool.txt_to_las input.txt -v Temperature_Met

# LAS to COPC
python -m calipso_tool.las_to_copc input.las

# Batch COPC conversion
python -m calipso_tool.las_to_copc . --batch
```

## Python API Usage

### Complete pipeline example:
```python
from calipso_tool.converter import h4_to_copc

# One-step conversion
copc_file, h5_file, txt_file, las_file = h4_to_copc(
    "CALIPSO_file.hdf",
    variable_name="Extinction_Coefficient_532",
    keep_intermediates=True
)
```

### Step-by-step example:
```python
from calipso_tool.converter import h4_to_h5
from calipso_tool.h5_to_txt import h5_to_txt
from calipso_tool.txt_to_las import txt_to_las_pipeline
from calipso_tool.las_to_copc import las_to_copc_pipeline

# Step 1: HDF4 to HDF5
h5_file = h4_to_h5(Path("input.hdf"), Path("output.h5"))

# Step 2: HDF5 to text
txt_file = h5_to_txt(h5_file, variable_name="Extinction_Coefficient_532")

# Step 3: Text to LAS
las_file = txt_to_las_pipeline(txt_file, variable_name="Extinction_Coefficient_532")

# Step 4: LAS to COPC
copc_file = las_to_copc_pipeline(las_file)
```

## Data Download

The package includes support for downloading CALIPSO data using NASA Earthdata:

```python
from earthaccess import Auth, search_data, download
import datetime

# Authenticate
auth = Auth()
auth.login(strategy="netrc")

# Search for data
results = search_data(
    short_name="CAL_LID_L3_Tropospheric_APro_AllSky-Standard-V4-20",
    temporal=(datetime.datetime(2019,1,1), datetime.datetime(2019,5,31)),
    bounding_box=(-125.0, 24.0, -66.5, 49.5)  # US bbox
)

# Download
for granule in results:
    local_paths = download([granule], local_path=Path("./data"))
```

## Output Formats

### HDF5
- Preserves all original HDF4 data
- More efficient and modern format
- Compatible with h5py and other tools

### Text (ASCII)
- Space-delimited columns: X, Y, Z, variable
- Human-readable format
- Compatible with many point cloud tools

### LAS
- Industry-standard point cloud format
- Includes coordinate scaling
- Supports extra dimensions for variables

### COPC (Cloud-Optimized Point Cloud)
- LAZ-compressed for 50-90% size reduction
- Hierarchical structure for streaming
- Optimized for cloud storage and web viewing
- Compatible with modern GIS software

## Troubleshooting

### Common Issues

1. **Variable not found error**
   - Use h5py to explore HDF5 structure
   - Ensure variable name matches exactly
   - Check for 3D variables only

2. **PDAL not found**
   - Install with: `conda install -c conda-forge pdal`
   - Verify installation: `pdal --version`

3. **Binary not found**
   - Ensure package is properly installed
   - Check bin/ directory in package

4. **Memory issues with large files**
   - Process files individually
   - Use batch processing with cleanup
   - Consider chunking large datasets

## Performance Tips

1. **Batch Processing**: Use provided batch functions for multiple files
2. **Cleanup**: Set `keep_intermediates=False` to save disk space
3. **Compression**: COPC format typically achieves 50-90% compression
4. **Parallel Processing**: Use concurrent.futures for multiple files

## Dependencies

- **Python**: numpy, pandas, h5py, laspy, click
- **System**: PDAL (with Python bindings)
- **Optional**: earthaccess, rioxarray (for data download)
- **Included**: h4toh5convert binary

## Future Enhancements

- Support for additional CALIPSO products
- Custom filtering and decimation options
- Direct streaming to cloud storage
- Web-based visualization tools