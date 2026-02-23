import pytest
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'churn_api.settings')
django.setup()

import mongomock
from unittest.mock import patch

@pytest.fixture(autouse=True)
def mock_mongo():
    with patch('analytics.db.MongoClient', mongomock.MongoClient):
        yield
