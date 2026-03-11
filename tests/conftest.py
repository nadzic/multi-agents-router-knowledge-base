"""Test configuration for local module imports."""

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MY_AGENT_DIR = PROJECT_ROOT / "my_agent"

if str(MY_AGENT_DIR) not in sys.path:
  sys.path.insert(0, str(MY_AGENT_DIR))
