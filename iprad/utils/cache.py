import os
import json
import requests
import whois
from dotenv import load_dotenv, find_dotenv
from os import getenv

from pathlib import Path
from datetime import datetime
from rich.console import Console


CACHE = Path(__file__).parent.parent.parent / '.cache'
console = Console()

load_dotenv(find_dotenv())
ABUSEIPDB_API_KEY = getenv("ABUSEIPDB_API_KEY")

def fetch(url: str, module_name: str, ip: str) -> str:
    try:
        if module_name not in ['whois', 'abuseipdb']:
            response = requests.get(url)
            response.raise_for_status()

            data = response.json()
        else:
            if module_name == 'whois':
                data = whois.whois(ip)

            if module_name == 'abuseipdb':
                params = {
                    'ipAddress': ip,
                    'maxAgeInDays': 180,
                }
                
                headers = {
                    'Key': ABUSEIPDB_API_KEY,
                    'Accept': 'application/json' 
                }
                
                response = requests.get(url, params=params, headers=headers)
                response.raise_for_status()
                
                data = response.json()



        return data

               
    except requests.exceptions.HTTPError as e:
            console.print(f"[bold red]HTTP ERROR![/] Failed to fetch data. Status: {response.status_code}")
    except requests.exceptions.ConnectionError:
            console.print("[bold red]CONNECTION ERROR![/] Check internet connection")
    except Exception as e:
            console.print(f"[bold red]ERROR![/] {str(e)}")

    return None
    
def json_serial(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def cache_processing(module_name: str, identifier: str, url=None):
    #Cache function
    cache_file = CACHE / module_name / f"{identifier}.json"
    module_dir = CACHE / module_name

    from_cache = False

    if cache_file.exists():
        with open(cache_file, 'r') as f:
            from_cache = True
            return json.load(f), from_cache

        
    #identifier = ip
    data = fetch(url, module_name, identifier)
    if data is None:
        return None, None     

    #Writing data to cache
    if data:
        module_dir.mkdir(parents=True, exist_ok=True)
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False, default=json_serial)
    else:
        console.print("[bold red]DATA PROCESSING ERROR![/]")

    

    return data, from_cache
                
