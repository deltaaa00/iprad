from rich.console import Console
from rich.panel import Panel
from iprad.utils.cache import cache_processing
from iprad.utils.functions import get_flag, get_resolved_ip

#IPinfo module
class IPinfoClient:
    BASE_URL = "https://ipinfo.io/"

    def check_ip(self, ip: str):

        #resolve ip 
        ip_resolved = get_resolved_ip(ip)
        
        url = f"{self.BASE_URL}/{ip_resolved}/json"
        
        console = Console()
        
        #Fetching data from ipinfo.io
        with console.status("[bold green]Fetching and processing Data...") as status:
            
            data, from_cache = cache_processing("ipinfo", ip, url)

            if data is None:
                return None

            info = (
                f"[bold green]IP:[/] {data.get('ip')}\n"
                f"[bold green]Hostname:[/] {data.get('hostname')}\n"
                f"[bold green]Provider:[/] {data.get('org')}\n\n"

                f"[bold cyan]City:[/] {data.get('city')}\n"
                f"[bold cyan]Region:[/] {data.get('region')}\n"
                f"[bold cyan]Country:[/] {data.get('country')} {get_flag(data.get('country'))}\n\n"
                
                f"[bold yellow]Timezone:[/] {data.get('timezone')}\n"
                f"[bold yellow]Location:[/] {data.get('loc')}\n"
                f"[bold yellow]Postal code:[/] {data.get('postal')}\n\n"

                f"[bold purple]Anycast:[/] {data.get('anycast')}"
            )



        console.print(Panel(info, title=f"[bold cyan]IPInfo Report for {ip} ({data.get('ip')})", subtitle=f"[bold blue]From Cache: [/] {from_cache}"))