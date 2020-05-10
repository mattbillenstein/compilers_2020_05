import io
import os
import time

import pytest
from wabbit.parse import parse_file
from wabbit.cyth import transpile_program
import subprocess
here = os.path.dirname(os.path.abspath(__file__))
script_location = os.path.join(here, 'Script')
function_location = os.path.join(here, 'Func')
wabbit_files = [os.path.join(script_location, name) for name in os.listdir(script_location) if name.endswith('wb')]
func_files = [os.path.join(function_location, name) for name in os.listdir(function_location) if name.endswith('wb')]

sillywabbit_location = os.path.abspath(os.path.join(here, '..', 'SillyWabbit'))
silly_wabbit_files = [os.path.join(sillywabbit_location, name) for name in os.listdir(sillywabbit_location) if name.endswith('wb')]

import contextlib
from unittest import mock

class MockPrint:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.calls = []
    def __call__(self, *args, **kwargs):
        if args == (True,):
            args = ('true',)
        if args == (False,):
            args = ('false', )
        self.calls.append((args, kwargs))

    def assert_called_with(self, *args, **kwargs):
        for c in self.calls:
            if c == (args, kwargs):
                return True
        raise AssertionError(f'Expected ({args}, {kwargs}). All calls: {self.calls}')

@pytest.mark.parametrize('fp', wabbit_files)
def test_wabbits(fp):
    expected_file = fp.replace('.wb', '.out')
    with open(expected_file) as f:
        expected_out = f.read()
    model = parse_file(fp)
    transpile_program(model)
    subprocess.run('python setup.py build_ext --inplace', check=True)
    time.sleep(1)
    res = subprocess.run(['python', '-c', 'import out'], check=True, capture_output=True)
    output = res.stdout.decode('utf-8')
    assert expected_out == output.replace('\r\n', '\n')

@pytest.mark.parametrize('fp', func_files + silly_wabbit_files)
def test_funcs(fp):
    model = parse_file(fp)
    transpile_program(model)