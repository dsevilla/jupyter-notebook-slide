import pytest

import notebook_slide


@pytest.fixture(autouse=True)
def clean_registry():
    """Every test starts from the default theme and slide types."""
    notebook_slide.reset()
    yield
    notebook_slide.reset()
