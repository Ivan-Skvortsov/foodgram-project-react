import pytest


@pytest.fixture
def guest_client():
    from rest_framework.test import APIClient
    return APIClient()
