#  Copyright 2023 Canonical Ltd.
#  See LICENSE file for licensing details.
"""Common functions for testing the sql group provider."""

import pytest
from flask import Flask

from tests.common import setup_sqlite


@pytest.fixture(name="app")
def app_fixture():
    """Create a flask app with a properly setup sqlite db."""
    app = Flask("test")
    setup_sqlite(app)
    return app
