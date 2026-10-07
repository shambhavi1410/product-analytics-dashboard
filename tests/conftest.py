import os

import pytest


@pytest.fixture(scope="session", autouse=True)
def sample_db(tmp_path_factory):
    """Build a small synthetic database once, and point the API at it."""
    from scripts.generate_sample_data import generate
    from scripts.load_data import load

    d = tmp_path_factory.mktemp("data")
    generate(d / "raw", orders=3000, seed=1)
    load(d / "raw", d / "olist.db")
    os.environ["DB_PATH"] = str(d / "olist.db")
