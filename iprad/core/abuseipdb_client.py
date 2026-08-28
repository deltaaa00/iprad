from rich.console import Console
from rich.panel import Panel
from iprad.utils.cache import cache_processing
from iprad.utils.functions import get_flag, get_resolved_ip
from dotenv import load_dotenv, find_dotenv
from os import getenv
from rich import print as rprint

#AbuseIPDB module
class AbuseIPDBClient:
    def __init__(self):
        load_dotenv(find_dotenv())
        self.API_KEY = getenv("ABUSEIPDB_API_KEY")

    def check_ip(self, ip: str):

        if not self.API_KEY:
            rprint("[bold red]Error: ABUSEIPDB_API_KEY not found in environment variables. Please set it in your .env file.")
            return None

        url = "https://api.abuseipdb.com/api/v2/check"

        #resolve ip 
        ip_resolved = get_resolved_ip(ip)
        
        console = Console()
         
        #Fetching data
        with console.status("[bold green]Fetching and processing Data...") as status:
            
            data_raw, from_cache = cache_processing("abuseipdb", ip, url)
        
            if data_raw is None:
                return None
            
            data = data_raw.get('data')

            score_emoji = "✅" if data.get('abuseConfidenceScore') < 20 else "⚠️" if data.get('abuseConfidenceScore') < 50 else "❌"

            info =  (
                    f"[bold green]IP:[/] {data.get('ipAddress')}\n"
                    f"[bold green]Score:[/] {data.get('abuseConfidenceScore')} {score_emoji}\n"
                    f"[bold green]Is Tor node:[/] {data.get('isTor')}\n\n"

                    f"[bold cyan]Total reports:[/] {data.get('totalReports')}\n"
                    f"[bold cyan]Last reported at:[/] {data.get('lastReportedAt')}\n"
                    f"[bold cyan]Distinct users:[/] {data.get('numDistinctUsers')}\n\n"

                    f"[bold yellow]Type:[/] {data.get('usageType')}\n"
                    f"[bold yellow]Domain:[/] {data.get('domain')} {get_flag(data.get('country'))}\n\n"

                    f"[bold purple]Is public:[/] {data.get('isPublic')}")


        console.print(Panel(info, title=f"[bold magenta]AbuseIPDB Report for {ip} ({data.get('ipAddress')}) (API key needed)", subtitle=f"[bold blue]From Cache: [/] {from_cache}"))