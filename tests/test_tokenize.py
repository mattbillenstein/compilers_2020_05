import pytest
import os
from wabbit.tokenize import main


@pytest.mark.parametrize('filename', [f'SillyWabbit/{name}' for name in os.listdir('SillyWabbit') if name.endswith('.wb')])
def test_tokenizefiles(filename):
    main(filename)

