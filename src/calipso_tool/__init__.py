import logging
import sys

# Configure logger for the calipso_tool package
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO) # Default level, can be configured further

# Create a handler for console output
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Prevent multiple handlers if __init__ is loaded multiple times in some scenarios
logger.propagate = False
