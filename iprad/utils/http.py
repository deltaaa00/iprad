"""HTTP GET requests with bounded retries and per-attempt timeouts."""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def get_json(url, *, retries=2, timeout=10, **kwargs):
    retry = Retry(
        total=retries,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET"}),
        respect_retry_after_header=False,
    )
    with requests.Session() as session:
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        response = session.get(url, timeout=timeout, **kwargs)
        response.raise_for_status()
        return response.json()
