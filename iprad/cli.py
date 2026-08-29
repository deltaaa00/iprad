import os
import click
import shutil
from iprad.core.ipinfo_client import IPinfoClient
from iprad.core.whois_client import WhoIsClient
from iprad.core.ping_tracert_client import PingTracertClient
from iprad.core.abuseipdb_client import AbuseIPDBClient

@click.group(invoke_without_command=True)
@click.pass_context

def main(ctx) -> None:
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@main.command()
@click.argument('ip', required=True)
@click.option('-pt', is_flag=True, help="Use ping and traceroute module, require sudo mode")
@click.option('--nokeys', is_flag=True, help="Run without API key")
def check(ip: str, pt: bool, nokeys: bool) -> None:
    if ip == "myip":
        import requests
        response = requests.get("https://api.ipify.org?format=json")
        if response.status_code == 200:
            ip = response.json().get("ip")
        else:
            click.echo("Failed to retrieve your IP address.")
            return
        
    client_ipinfo = IPinfoClient()
    client_ipinfo.check_ip(ip)

    client_whois = WhoIsClient()
    client_whois.check_ip(ip)

    if not nokeys:
        client_abuseipdb = AbuseIPDBClient()
        client_abuseipdb.check_ip(ip)

    #user can use ping and tracert
    if pt:
        client_ping = PingTracertClient()
        client_ping.check_ip(ip)

@main.command()
def self():
    from iprad.core.device_info_client import SelfInfoClient
    client_self = SelfInfoClient()
    client_self.check_ip()


@click.group(invoke_without_command=True)
@click.pass_context
def cache(ctx):
    """Cache manager"""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())

main.add_command(cache)

@cache.command('rm', help="Delete cache files")
def delete() -> None:

    from iprad.utils.cache import CACHE
    from rich.console import Console

    #Checking if cache exist
    console = Console()
    if CACHE.exists():
        try:
            shutil.rmtree(CACHE)

            console.print("[bold green] Cache removed successfully")

        except Exception as e:
            console.print(f"[bold red] Cache wasn`t removed due {e}")
    else:
        console.print(f"[bold purple] There aren`t any cache files! ")

@cache.command('info', help="Cache info")
def cache_status() -> None:
    from iprad.utils.cache import CACHE
    from rich.console import Console

    # Checking if cache exist
    console = Console()
    if CACHE.exists():
        total_bytes = 0
        for root, dirs, files in os.walk(CACHE):
            for file in files:
                file_path = os.path.join(root, file)
                # Перевіряємо, що це файл і він існує
                if os.path.isfile(file_path):
                    total_bytes += os.path.getsize(file_path)

        console.print(f"Cache Size: [bold green] {total_bytes / (1024 * 1024):.4f}MB")
    else:
        console.print(f"[bold red] Cache doesn`t exist")
