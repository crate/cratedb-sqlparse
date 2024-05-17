import subprocess
import sys
from pathlib import Path

import pytest


HERE = Path(__file__).parent
PROJECT_ROOT = HERE.parent.parent
SETUP_GRAMMAR = PROJECT_ROOT / "setup_grammar.py"


@pytest.fixture(scope="session", autouse=True)
def generate():
    """
    Pytest fixture to generate runtime grammar from grammar description.
    """
    try:
        import cratedb_sqlparse.generated_parser.SqlBaseParser
    except ImportError:
        subprocess.check_call([sys.executable, SETUP_GRAMMAR], cwd=HERE.parent.parent)

    try:
        import cratedb_sqlparse.generated_parser.SqlBaseParser
    except ImportError:
        raise RuntimeError("Python grammar has not been generated")
