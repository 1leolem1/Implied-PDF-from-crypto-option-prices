import requests
import pytest
from tests import get_api_data

# Import the function to test from the absolute module "tests"
# (Assuming that tests.py defines a function named get_api_data that fetches API data.)


def test_get_api_data_is_callable():
    # Ensure the function is imported correctly and is callable.
    assert callable(get_api_data)


def test_api_reachable_via_get_api_data():
    # Call the function and validate that it returns a non‐empty dict,
    # which implies that the API call within get_api_data succeeded.
    data = get_api_data()
    assert isinstance(data, dict)
    assert data  # Checks that the dict is not empty


def test_github_api_reachable():
    # Directly test that a known API endpoint (GitHub's API) is reachable.
    response = requests.get("https://api.github.com")
    assert response.status_code == 200
