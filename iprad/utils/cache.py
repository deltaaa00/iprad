import json
import requests
import re
from dotenv import load_dotenv, find_dotenv
from os import getenv
from iprad.utils.functions import normalize_rdap_data
from iprad.utils.http import get_json

from pathlib import Path
from datetime import datetime
from rich.console import Console


CACHE = Path(__file__).parent.parent.parent / '.cache'
console = Console()

load_dotenv(find_dotenv())

def fetch(url: str, module_name: str, ip: str, *, retries=2, timeout=10):
    try:
        kwargs = {}
        if module_name == 'abuseipdb':
            kwargs = {
                "params": {"ipAddress": ip, "maxAgeInDays": 180},
                "headers": {"Key": getenv("ABUSEIPDB_API_KEY"), "Accept": "application/json"},
            }
        data = get_json(url, retries=retries, timeout=timeout, **kwargs)
        data['created_at'] = datetime.now()
        if module_name == 'whois':
            data = normalize_rdap_data(data, ip)
        return data
    except requests.exceptions.RequestException as exc:
        console.print("HTTP request failed:", str(exc), style="bold red", markup=False)
    except (ValueError, TypeError) as exc:
        console.print("Invalid API response:", str(exc), style="bold red", markup=False)
    return None

def json_serial(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def cache_processing(module_name: str, identifier: str, url=None, *,
                     refresh=False, cache_ttl=48, retries=2, timeout=10):
    #Cache function
    safe_identifier = re.sub(r"[^a-zA-Z0-9_-]", "_", identifier)
    cache_file = CACHE / module_name / f"{safe_identifier}.json"
    module_dir = CACHE / module_name

    from_cache = False

    if cache_file.exists() and not refresh:
        try:
            with cache_file.open() as handle:
                data = json.load(handle)
            created_at = datetime.fromisoformat(data["created_at"])
            age = (datetime.now(created_at.tzinfo) - created_at).total_seconds() / 3600
            if 0 <= age < cache_ttl:
                return data, True
        except (ValueError, KeyError, TypeError, AttributeError):
            pass  # A malformed cache entry should not prevent a fresh lookup.
        cache_file.unlink()

    data = fetch(url, module_name, identifier, retries=retries, timeout=timeout)

    if data is None:
        return None, None

    #adding cache create time

    data['created_at'] = datetime.now()


    #Writing data to cache
    if data:
        module_dir.mkdir(parents=True, exist_ok=True)
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False, default=json_serial)
    else:
        console.print("[bold red]DATA PROCESSING ERROR![/]")

    

    return data, from_cache
                
