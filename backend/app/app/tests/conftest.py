from typing import Dict, Generator

import pytest
from starlette.testclient import TestClient
from app.core.config import settings
from app.main import app


@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c
