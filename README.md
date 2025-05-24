**CALIPSO Conversion Toolkit**

A minimal, reproducible Python package for converting CALIPSO HDF4 aerosol data through an end-to-end workflow:

* **HDF4 → HDF5** using the `h4toh5convert` binary.
* **HDF5 → ASCII** extracting latitude, longitude, altitude, and sample value grids into a text file.
* **ASCII → LAS/COPC** via PDAL pipelines for point cloud generation (including extra dims).

---

## Features

* **Single CLI entry point (`calipso-convert`)** for HDF4 → HDF5 conversion; future releases will chain subsequent steps.
* **Vendored or conda-managed `h4toh5convert` binary**, so users need not install HDF4/HDF5 tools separately. Binary obtained from [HDF Group](https://support.hdfgroup.org/downloads/h4h5tools/h4h5tools_2_2_5.html)
* **Configurable ASCII exporter** supports any 3D variable (e.g., `Samples_Averaged`, `Extinction_Coefficient_532_Mean`).
* **PDAL integration** with pre-defined JSON pipelines:

  * `h5tolas.json` for reading text and writing LAS with extra dimensions.
  * `las2copc.json` for converting LAS to Cloud-Optimized Point Cloud (COPC).
* **Conda environment specification** (`environment.yml`) for reproducibility across platforms.
* **Editable install** via `uv pip install -e .`, enabling rapid development and collaboration.

---

## Getting Started

### Prerequisites

* [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or \[Anaconda].
* macOS or Linux (Windows support TBD).

### Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/your-org/calipso-convert.git
   cd calipso-convert
   ```

2. **Create and activate the Conda environment**:

   ```bash
   conda env create -f environment.yml
   conda activate cali-tool-env
   ```

3. **Install the package in editable mode**:

   ```bash
   uv pip install -e .
   ```

4. **Verify the CLI**:

   ```bash
   cali-convert --help
   ```

---

## Usage Example

```bash
# Convert a CALIPSO HDF4 file to HDF5:
$ cali-convert path/to/CAL_LID_L3_Tropospheric_APro_AllSky-Standard-V4-20.2018-12D.hdf
Converting CAL_LID_L3_Tropospheric_APro_AllSky-Standard-V4-20.2018-12D.hdf → CAL_LID_…2018-12D.h5
Done!

# Now generate ASCII:
$ python -m cali_tool.export_ascii --input CAL_LID_…2018-12D.h5 --output points.txt --variable Samples_Averaged

# Create a LAS point cloud:
$ pdal pipeline pipe.json --readers.text.filename=points.txt --writers.las.filename=points.las

# Generate a COPC point cloud:
$ pdal pipeline copc.json --readers.las.filename=points.las --writers.copc.filename=points.copc.laz
```

---

## Project Structure

```text
calipso-convert/
├── environment.yml         # Conda environment spec
├── pyproject.toml          # Package metadata & CLI entry points
├── README.md               # This file
└── src/
    └── cali_tool/
        ├── bin/            # h4toh5convert (vendored binary)
        ├── cli.py          # CLI entry-point implementation
        ├── converter.py    # HDF4→HDF5 conversion logic
        ├── export_ascii.py # HDF5→ASCII exporter
        └── pipelines/
            ├── pipe.json   # ASCII→LAS PDAL pipeline
            └── copc.json   # LAS→COPC PDAL pipeline
```

---

## Development

1. **Edit code** in `src/cali_tool/`.
2. **Write tests** under `tests/` (TBD).
3. **Run linters & formatters**:

   ```bash
   flake8 src tests
   black src tests
   ```
4. **Publish** new versions:

   ```bash
   git tag v0.2.0
   git push --tags
   ```

---

## License

MIT © Your Name

---

## Acknowledgments

* PDAL for point cloud tools
* laspy for LAS I/O
* h5py / pyhdf for HDF handling

