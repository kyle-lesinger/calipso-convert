# CALIPSO Conversion Toolkit

A comprehensive Python package for converting CALIPSO HDF4 atmospheric data through a complete point cloud processing pipeline:

**HDF4 → HDF5 → Text → LAS → COPC**

Transform CALIPSO atmospheric aerosol and cloud data into modern, cloud-optimized point cloud formats suitable for 3D visualization and GIS analysis.

---

## 🚀 Features

* **Complete Pipeline** - One-command conversion from HDF4 to Cloud-Optimized Point Cloud (COPC)
* **Flexible Processing** - Run individual steps or the complete pipeline
* **Variable Selection** - Extract any 3D variable from CALIPSO data (e.g., `Extinction_Coefficient_532`, `Temperature_Met`)
* **NASA Earthdata Integration** - Built-in support for downloading CALIPSO data
* **Batch Processing** - Convert multiple files efficiently
* **PDAL Integration** - Leverages PDAL for robust point cloud generation
* **Cloud-Ready Output** - COPC format optimized for streaming and web visualization
* **Cross-Platform** - Works on macOS, Linux, and Windows (with WSL)

---

## 📦 Installation

### Prerequisites

* Python 3.10+
* [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Anaconda](https://www.anaconda.com/)
* PDAL (installed via conda)

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-org/calipso-convert.git
   cd calipso-convert
   ```

2. **Create and activate the Conda environment**:
   ```bash
   conda env create -f environment.yml
   conda activate calipso-tool-env
   ```

3. **Install the package**:
   ```bash
   uv pip install -e .
   ```

4. **Verify installation**:
   ```bash
   cali-convert --help
   ```

---

## 🎯 Usage Examples

### One-Step Complete Pipeline

Convert CALIPSO HDF4 directly to COPC:

```python
from calipso_tool.converter import h4_to_copc

# Complete conversion in one line
copc_file, _, _, _ = h4_to_copc(
    "CAL_LID_L3_Tropospheric_APro_AllSky-Standard-V4-20.2018-12D.hdf",
    variable_name="Extinction_Coefficient_532",
    keep_intermediates=False
)
```

### Command Line Usage

```bash
# Basic HDF4 to HDF5 conversion
cali-convert input.hdf

# Complete pipeline with specific variable
python -m calipso_tool.converter input.hdf -v Extinction_Coefficient_532
```

### Step-by-Step Processing

```python
from calipso_tool.converter import h4_to_h5
from calipso_tool.h5_to_txt import h5_to_txt
from calipso_tool.txt_to_las import txt_to_las_pipeline
from calipso_tool.las_to_copc import las_to_copc_pipeline

# Step 1: HDF4 to HDF5
h5_file = h4_to_h5(Path("input.hdf"), Path("output.h5"))

# Step 2: HDF5 to text (extract 3D variable)
txt_file = h5_to_txt(h5_file, variable_name="Extinction_Coefficient_532")

# Step 3: Text to LAS
las_file = txt_to_las_pipeline(txt_file, variable_name="Extinction_Coefficient_532")

# Step 4: LAS to COPC
copc_file = las_to_copc_pipeline(las_file)
```

### Download CALIPSO Data

```python
from earthaccess import Auth, search_data, download
import datetime

# Authenticate with NASA Earthdata
auth = Auth()
auth.login(strategy="netrc")

# Search for CALIPSO data
results = search_data(
    short_name="CAL_LID_L3_Tropospheric_APro_AllSky-Standard-V4-20",
    temporal=(datetime.datetime(2019,1,1), datetime.datetime(2019,5,31)),
    bounding_box=(-125.0, 24.0, -66.5, 49.5)  # US bounding box
)

# Download files
for granule in results:
    download([granule], local_path=Path("./data"))
```

---

## 📁 Project Structure

```
calipso-convert/
├── environment.yml              # Conda environment specification
├── pyproject.toml              # Package metadata & dependencies
├── README.md                   # This file
├── src/
│   └── calipso_tool/
│       ├── __init__.py        # Package initialization
│       ├── cli.py             # CLI entry point
│       ├── converter.py       # Main conversion orchestrator
│       ├── h5_to_txt.py       # HDF5 to text converter
│       ├── txt_to_las.py      # Text to LAS converter
│       ├── las_to_copc.py     # LAS to COPC converter
│       ├── DOCUMENTATION.md   # Detailed API documentation
│       └── bin/
│           └── h4toh5convert  # Vendored HDF4-to-HDF5 binary
├── notebooks/                  # Example Jupyter notebooks
│   ├── CALIPSO_download.ipynb
│   ├── test-hdf-to-hdf5-conversion.ipynb
│   ├── test-hdf5-to-txt-conversion.ipynb
│   ├── test-hdf-to-txt-conversion.ipynb
│   ├── test-txt-to-las-conversion.ipynb
│   ├── test-las-to-copc-conversion.ipynb
│   └── test-hdf-to-copc-conversion.ipynb
└── tests/                      # Unit tests (TBD)
```

---

## 🔧 Advanced Features

### Batch Processing

Convert multiple CALIPSO files:

```python
from pathlib import Path
from calipso_tool.converter import h4_to_copc

for hdf_file in Path("./data").glob("*.hdf"):
    copc_file, _, _, _ = h4_to_copc(
        hdf_file,
        variable_name="Extinction_Coefficient_532",
        keep_intermediates=False
    )
    print(f"Converted {hdf_file.name} → {copc_file.name}")
```

### Custom PDAL Pipelines

Create custom processing pipelines:

```python
from calipso_tool.txt_to_las import txt_to_las

# Custom scaling for higher precision
las_file = txt_to_las(
    "input.txt",
    variable_name="Temperature_Met",
    scale_x=1e-6,  # Longitude precision
    scale_y=1e-6,  # Latitude precision  
    scale_z=0.001, # Altitude precision (mm)
    srs="EPSG:4326"
)
```

### Available Variables

Common CALIPSO L3 variables for extraction:
- `Extinction_Coefficient_532` - Aerosol extinction at 532nm
- `Temperature_Met` - Meteorological temperature
- `Pressure_Met` - Meteorological pressure
- `Relative_Humidity` - Relative humidity
- `Samples_Averaged` - Number of averaged samples

---

## 📊 Output Formats

### HDF5
- Modern hierarchical data format
- Preserves all original CALIPSO data
- Compatible with Python, MATLAB, IDL

### Text (ASCII)
- Space-delimited columns: X, Y, Z, variable
- Human-readable format
- Compatible with many GIS tools

### LAS
- Industry-standard point cloud format
- Includes coordinate scaling and georeferencing
- Supports extra dimensions for atmospheric variables

### COPC (Cloud-Optimized Point Cloud)
- 50-90% compression vs standard LAS
- Streamable format for web visualization
- Compatible with Potree, QGIS, CloudCompare
- Optimized for cloud storage (S3, Azure, GCS)

---

## 🛠️ Development

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=calipso_tool tests/
```

### Code Style

```bash
# Format code
black src/ tests/

# Check linting
flake8 src/ tests/

# Type checking
mypy src/
```

---

## 📚 Documentation

- [Detailed API Documentation](src/calipso_tool/DOCUMENTATION.md)
- [Example Notebooks](notebooks/)
- [CALIPSO Data Guide](https://www-calipso.larc.nasa.gov/resources/calipso_users_guide/)

---

## 🔗 Dependencies

- **Core**: numpy, pandas, h5py, click
- **Point Clouds**: laspy, pdal
- **Data Access**: earthaccess, rioxarray
- **Notebooks**: jupyter, ipykernel
- **Included**: h4toh5convert binary

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

---

## 🙏 Acknowledgments

- [NASA CALIPSO Mission](https://www-calipso.larc.nasa.gov/) for atmospheric data
- [PDAL Contributors](https://pdal.io/) for point cloud processing tools
- [HDF Group](https://www.hdfgroup.org/) for h4toh5convert utility
- [Laspy Developers](https://github.com/laspy/laspy) for LAS file support
- [COPC Specification](https://copc.io/) for cloud-optimized format

---

## 📮 Contact

Kyle Lesinger - kdl0040@uah.edu

Project Link: [https://github.com/your-org/calipso-convert](https://github.com/your-org/calipso-convert)