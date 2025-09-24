import os

def test_no_duplicate_dependencies():
    """
    Tests that there are no duplicate dependencies in requirements/base.txt.
    """
    requirements_file = os.path.join(os.path.dirname(__file__), '..', '..', 'requirements', 'base.txt')
    with open(requirements_file, 'r') as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    assert len(lines) == len(set(lines)), "Duplicate dependencies found in requirements/base.txt"
