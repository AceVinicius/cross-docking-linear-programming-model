import pytest

from io import StringIO
from instance import go_to_next_info


def test_go_to_next_info_with_empty_line():
    # Create a file-like object with contents
    file_contents = "\nSection 1\n"
    file = StringIO(file_contents)

    # Read the first section
    go_to_next_info(file)

    # Ensure we are at the second section
    assert file.readline().strip() == "Section 2"

def test_go_to_next_info_without_empty_line():
    # Create a file-like object with contents
    file_contents = "Section 1\n"
    file = StringIO(file_contents)

    # Ensure that an error is raised if there is no empty line
    with pytest.raises(ValueError):
        go_to_next_info(file)

def test_go_to_next_info_without_title():
    # Create a file-like object with contents
    file_contents = "\nSection 1\n\n"
    file = StringIO(file_contents)

    # Ensure that an error is raised if there is no title
    with pytest.raises(ValueError):
        go_to_next_info(file)

def test_go_to_next_info_with_multiple_empty_lines():
    # Create a file-like object with contents
    file_contents = "\n\nSection 1\n"
    file = StringIO(file_contents)

    # Ensure we can skip multiple empty lines
    go_to_next_info(file)

    # Ensure we are at the second section
    assert file.readline().strip() == "Section 2"
