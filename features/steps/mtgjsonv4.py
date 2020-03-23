""" MTGJSONv4 Integration Tests """
from behave import *
import subprocess
from subprocess import Popen, PIPE

from pathlib import Path
from mtgjson4 import COMPILED_OUTPUT_DIR

@given('we install mtgjson')
def step_impl(context) -> None:
    """
    Install module
    """
    subprocess.run(['pip', 'install', '.'])

@given('we build a v4 argument')
def step_impl(context):
    """
    Add v4 as version
    """
    context.cli_args['-m'] = 'mtgjson4'

@when('we include the skip-keys argument')
def step_impl(context):
    """
    Add skip keys argument
    """
    context.cli_args['--skip-keys'] = ''

@when('we build a {set_code:w} argument')
def step_impl(context, set_code):
    """
    Build a set
    """
    context.cli_args['-s'] = set_code

@when('we run the cli')
def step_impl(context):
    """
    Run the cli
    """
    cli_args = ['python'] + [f"{k} {v}" for (k, v) in context.cli_args.items()]
    subprocess.check_call(' '.join(cli_args), shell=True)

@then('we will render the set to {set_json_file:w}')
def step_impl(context, set_json_file):
    """
    Assert file was rendered
    """
    json_file = Path(f"{COMPILED_OUTPUT_DIR}/{set_json_file}.json")
    assert json_file.is_file()
