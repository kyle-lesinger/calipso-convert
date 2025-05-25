import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Attempt to import the function to be tested
# This assumes your project structure allows this import from the tests directory
try:
    from calipso_tool.converter import h4_to_h5
except ImportError:
    # Fallback for environments where the package isn't installed in editable mode yet
    # This might require adjusting PYTHONPATH or your test runner configuration
    # For now, we'll define a placeholder if the import fails during development
    def h4_to_h5(in_h4: Path, out_h5: Path):
        print(f"Placeholder h4_to_h5 called with {in_h4} and {out_h5}")
        # Simulate the binary call for path checking if needed by other logic
        if not in_h4.exists(): # Simplified check
             raise FileNotFoundError(f"Input file {in_h4} not found.")
        # Simulate output file creation
        out_h5.touch() 
        return out_h5

# Define a fixture for temporary file paths
@pytest.fixture
def temp_files(tmp_path):
    input_hdf4 = tmp_path / "test_input.hdf"
    output_hdf5 = tmp_path / "test_output.h5"
    # Create a dummy input file for functions that check existence
    input_hdf4.touch()
    return input_hdf4, output_hdf5

def test_h4_to_h5_conversion_success(temp_files):
    """
    Test the h4_to_h5 function for successful conversion.
    Mocks subprocess.run and importlib.resources.files.
    """
    in_h4_path, out_h5_path = temp_files

    # Mock for importlib.resources.files().joinpath()
    mock_bin_path = MagicMock(spec=Path)
    mock_bin_path.__str__.return_value = "/fake/path/to/h4toh5convert" # Needed for subprocess.run

    # Patch importlib.resources.files to return our mock path object
    with patch('importlib.resources.files') as mock_files,          patch('subprocess.run') as mock_subprocess_run:

        # Configure mock_files to return an object that supports .joinpath()
        # and resolves to mock_bin_path
        mock_files.return_value.joinpath.return_value = mock_bin_path
        
        # Configure the mock for subprocess.run
        # Simulate a successful run (returncode=0)
        mock_subprocess_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)

        # Call the function
        result_path = h4_to_h5(in_h4_path, out_h5_path)

        # Assertions
        mock_files.assert_called_once_with("calipso_tool")
        mock_files.return_value.joinpath.assert_any_call("bin") # intermediate joinpath
        mock_files.return_value.joinpath.assert_any_call("h4toh5convert") # final joinpath

        mock_subprocess_run.assert_called_once_with(
            [str(mock_bin_path), str(in_h4_path), str(out_h5_path)],
            check=True
        )
        assert result_path == out_h5_path
        # In a real scenario with actual file creation, you might check if out_h5_path exists
        # but here subprocess.run is mocked, so it won't create the file.
        # If the function itself creates the file (e.g. out_h5.touch()), that's testable.

def test_h4_to_h5_conversion_failure_subprocess(temp_files):
    """
    Test the h4_to_h5 function when the subprocess call fails.
    """
    in_h4_path, out_h5_path = temp_files

    mock_bin_path = MagicMock(spec=Path)
    mock_bin_path.__str__.return_value = "/fake/path/to/h4toh5convert"

    with patch('importlib.resources.files') as mock_files,          patch('subprocess.run') as mock_subprocess_run:
        
        mock_files.return_value.joinpath.return_value = mock_bin_path
        
        # Simulate a failed run
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd=['/fake/path/to/h4toh5convert']
        )

        with pytest.raises(subprocess.CalledProcessError):
            h4_to_h5(in_h4_path, out_h5_path)
        
        mock_subprocess_run.assert_called_once_with(
            [str(mock_bin_path), str(in_h4_path), str(out_h5_path)],
            check=True
        )

# Example of how you might test if the input file doesn't exist,
# assuming h4_to_h5 or the binary it calls checks for this.
# This specific test might fail or pass depending on h4_to_h5's internal error handling
# or if the actual binary is called (which it isn't in the mocked tests above).
# For this example, we assume the function might raise FileNotFoundError if the binary isn't found
# or if the input path is invalid *before* the subprocess call, which is unlikely with current h4_to_h5 structure.
# The current h4_to_h5 relies on `subprocess.run` with `check=True` which handles the binary not found
# or the binary failing.

# If the binary itself handles input file checking, then a test for "input file not found"
# would look similar to test_h4_to_h5_conversion_success, but you'd set up the
# mock_subprocess_run to simulate the binary's specific error for a missing file.
# For instance, if the binary exits with a specific error code for "file not found":
# mock_subprocess_run.side_effect = subprocess.CalledProcessError(returncode=2, cmd=[...])
# and then you'd assert that your function correctly handles or propagates this.
