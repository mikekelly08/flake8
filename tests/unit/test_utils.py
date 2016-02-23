"""Tests for flake8's utils module."""
import os
import mock

import pytest

from flake8 import utils


RELATIVE_PATHS = ["flake8", "pep8", "pyflakes", "mccabe"]


@pytest.mark.parametrize("value,expected", [
    ("E123,\n\tW234,\n    E206", ["E123", "W234", "E206"]),
    ("E123,W234,E206", ["E123", "W234", "E206"]),
    (["E123", "W234", "E206"], ["E123", "W234", "E206"]),
    (["E123", "\n\tW234", "\n    E206"], ["E123", "W234", "E206"]),
])
def test_parse_comma_separated_list(value, expected):
    """Verify that similar inputs produce identical outputs."""
    assert utils.parse_comma_separated_list(value) == expected


@pytest.mark.parametrize("value,expected", [
    ("flake8", "flake8"),
    ("../flake8", os.path.abspath("../flake8")),
    ("flake8/", os.path.abspath("flake8")),
])
def test_normalize_path(value, expected):
    """Verify that we normalize paths provided to the tool."""
    assert utils.normalize_path(value) == expected


@pytest.mark.parametrize("value,expected", [
    ("flake8,pep8,pyflakes,mccabe", ["flake8", "pep8", "pyflakes", "mccabe"]),
    ("flake8,\n\tpep8,\n  pyflakes,\n\n    mccabe",
        ["flake8", "pep8", "pyflakes", "mccabe"]),
    ("../flake8,../pep8,../pyflakes,../mccabe",
        [os.path.abspath("../" + p) for p in RELATIVE_PATHS]),
])
def test_normalize_paths(value, expected):
    """Verify we normalize comma-separated paths provided to the tool."""
    assert utils.normalize_paths(value) == expected


def test_is_windows_checks_for_nt():
    """Verify that we correctly detect Windows."""
    with mock.patch.object(os, 'name', 'nt'):
        assert utils.is_windows() is True

    with mock.patch.object(os, 'name', 'posix'):
        assert utils.is_windows() is False


@pytest.mark.parametrize('filename,patterns,expected', [
    ('foo.py', [], True),
    ('foo.py', ['*.pyc'], False),
    ('foo.pyc', ['*.pyc'], True),
    ('foo.pyc', ['*.swp', '*.pyc', '*.py'], True),
])
def test_fnmatch(filename, patterns, expected):
    """Verify that our fnmatch wrapper works as expected."""
    assert utils.fnmatch(filename, patterns) is expected


def test_filenames_from_a_directory():
    """Verify that filenames_from walks a directory."""
    filenames = list(utils.filenames_from('flake8/'))
    assert len(filenames) > 2
    assert 'flake8/__init__.py' in filenames


def test_filenames_from_a_directory_with_a_predicate():
    """Verify that predicates filter filenames_from."""
    filenames = list(utils.filenames_from(
        arg='flake8/',
        predicate=lambda filename: filename == 'flake8/__init__.py',
    ))
    assert len(filenames) > 2
    assert 'flake8/__init__.py' not in filenames


def test_filenames_from_a_single_file():
    """Verify that we simply yield that filename."""
    filenames = list(utils.filenames_from('flake8/__init__.py'))

    assert len(filenames) == 1
    assert ['flake8/__init__.py'] == filenames
