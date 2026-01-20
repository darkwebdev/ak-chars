#!/usr/bin/env python3
"""Start the API server for integration tests with proper module path."""

import sys
import os
from pathlib import Path

# Add parent directory to path so server package can be imported
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Change to server directory for proper relative imports
os.chdir(project_root / 'server')

# Now import and run uvicorn
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "server.main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )
