from rich.console import Console
from rich.panel import Panel
from iprad.utils.functions import get_flag
from rich import print as rprint

import socket
import uuid
import requests
import psutil
import subprocess
import re

def get_gateway_ip():
    try:
        result = subprocess.check_output(
            ["ipconfig"],
            text=True,
            encoding="cp866"
        )

        match = re.search(
            r"Default Gateway[ .]*: ([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)",
            result
        )

        if match:
            return match.group(1)

    except Exception:
        pass

    return "Unknown"

class SelfInfoClient:
    def check_ip(self):

        
        console = Console()
         
        with console.status("[bold green]Fetching and processing Data...") as status:
    
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                    for ele in range(0, 8*6, 8)][::-1])
            
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)

            try:
                external_ip = requests.get('https://api.ipify.org', timeout=3).text
            except:
                external_ip = "[bold red]Offline[/bold red]"

            gateway = get_gateway_ip()

            info =  (

                    f"[bold green]Local IP:[/] {local_ip}\n"
                    f"[bold green]External IP:[/] {external_ip}\n"
                    f"[bold green]Gateway IP:[/] {gateway}\n\n"

                    f"[bold cyan]MAC Address:[/] {mac}\n"
                    f"[bold cyan]Hostname:[/] {hostname}\n"

                    f"[bold yellow]Interfaces: [/] {list(psutil.net_if_addrs().keys())}"
                    
                    )


        console.print(Panel(info, title=f"[bold magenta]Device Report", subtitle=f"[bold cyan] iprad - open-source IP Look up tool for OSINT and cybersecurity."))