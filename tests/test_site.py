import subprocess
import threading
import time
from typing import Generator

import pytest
import requests
from bs4 import BeautifulSoup

from main import Category, get_content


@pytest.fixture(scope="session")
def start_server() -> Generator[None, None, None]:
    # not sure how to do this better. I dont think Robyn has a mock server yet
    server_process = subprocess.Popen(["python", "main.py"])
    time.sleep(2)
    yield
    server_process.terminate()
    server_process.wait()


def test_site_index(start_server: None) -> None:
    response = requests.get("http://localhost:8081/")
    assert response.status_code == 200


@pytest.mark.parametrize("category", get_content())
def test_posts(start_server: None, category: Category) -> None:
    for post in category.posts:
        response = requests.get(f"http://localhost:8081/{category.name}/{post.id}")
        assert response.status_code == 200


@pytest.mark.skip(reason="not implemented")
def test_404(start_server: None) -> None:
    ...


@pytest.mark.skip(reason="not implemented")
def test_static(start_server: None) -> None:
    ...


@pytest.mark.skip(reason="not implemented")
def test_broken_links(start_server: None) -> None:
    ...


@pytest.mark.skip(reason="not implemented")
def test_broken_images(start_server: None) -> None:
    ...


@pytest.mark.parametrize("category", get_content())
def test_categories(start_server: None, category: Category) -> None:
    response = requests.get(f"http://localhost:8081/{category.name}")
    assert response.status_code == 200


@pytest.mark.parametrize("category", get_content())
def test_page_html_valid_posts(start_server: None, category: Category) -> None:
    for post in category.posts:
        response = requests.get(f"http://localhost:8081/{category.name}/{post.id}")
        soup = BeautifulSoup(response.content, "html.parser")
        assert soup


@pytest.mark.parametrize(
    "url",
    [
        "http://localhost:8081/",
    ],
)
def test_page_html_valid(start_server: None, url: str) -> None:
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    assert soup
