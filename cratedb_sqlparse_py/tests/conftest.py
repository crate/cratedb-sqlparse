import subprocess
import sys
from importlib.util import find_spec
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
        # Test module for availability.
        find_spec("cratedb_sqlparse.generated_parser.SqlBaseParser")
    except ImportError:
        subprocess.check_call([sys.executable, SETUP_GRAMMAR, "python"], cwd=HERE.parent.parent)  # noqa: S603

    try:
        # Test module for availability.
        find_spec("cratedb_sqlparse.generated_parser.SqlBaseParser")
    except ImportError as ex:
        raise RuntimeError("Python grammar has not been generated") from ex
