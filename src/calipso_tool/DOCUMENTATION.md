# CALIPSO Tool Documentation

## Overview
This package provides tools for converting CALIPSO HDF4 files to HDF5 format, with planned functionality for LAS and COPC conversion.

## Module Structure

### `__init__.py`
Empty module initialization file.

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

**Description:**
Processes the input HDF4 file and converts it to HDF5 format. The output file is created in the same directory as the input file with a .h5 extension.

**Example:**
```bash
cali-convert /path/to/input.hdf
# Output: /path/to/input.h5
```

### `converter.py`
Core conversion functionality for transforming HDF4 files to HDF5 format.

#### Functions

##### `h4_to_h5(in_h4: Path, out_h5: Path)`
Converts HDF4 files to HDF5 format using a vendored binary converter.

**Parameters:**
- `in_h4` (Path): Path object pointing to the input HDF4 file
- `out_h5` (Path): Path object where the output HDF5 file will be saved

**Returns:** Path - Returns the output path (out_h5) after successful conversion

**Description:**
This function:
1. Locates the vendored `h4toh5convert` binary included with the package
2. Executes the binary using subprocess to perform the conversion
3. Returns the output path upon successful completion

**Implementation Details:**
- Uses `importlib.resources.files()` to access the packaged binary
- Runs the conversion as a subprocess call
- The binary path is constructed relative to the calipso_tool package

**Note:** There's a missing import for `Path` in converter.py that should be fixed.

## Binary Dependencies

### `bin/h4toh5convert`
Vendored binary tool that performs the actual HDF4 to HDF5 conversion. This binary is included with the package and is automatically located by the converter module.

## Usage Flow

1. User invokes the CLI with: `cali-convert input.hdf`
2. CLI validates the input file exists and is not a directory
3. CLI creates output path by replacing extension with .h5
4. CLI calls `h4_to_h5()` function with input and output paths
5. Converter locates the vendored binary and executes it
6. Success message is displayed to the user
7. Program exits with status 0

## Future Enhancements
Based on the project description, planned features include:
- HDF5 to LAS conversion
- LAS to COPC conversion
- Complete workflow: HDF4 → HDF5 → LAS → COPC