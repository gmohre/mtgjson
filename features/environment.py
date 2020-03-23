""" Behave ENV """
import subprocess
from mtgjson4 import COMPILED_OUTPUT_DIR

def before_all(context) -> None:
    """
    Init CLI args for command
    """
    context.cli_args = {}

def after_all(context) -> None:
    """
    Cleanup files
    """
    subprocess.run(['rm', '-rf', COMPILED_OUTPUT_DIR])
