import whois

from rich.console import Console
from rich.panel import Panel
from iprad.utils.cache import cache_processing
from iprad.utils.functions import get_flag, get_resolved_ip

#Whois module

class WhoIsClient:
    def check_ip(self, ip: str):

        #resolve ip 
        ip_resolved = get_resolved_ip(ip)
        
        
        console = Console()
        # console.clear()
        
        #Fetching data from whois
        with console.status("[bold green]Fetching and processing Data...") as status:
            
            data, from_cache = cache_processing("whois", ip_resolved)

            
            if data is None:
                return None
            
            domain = data.get('domain_name')
            if isinstance(domain, list): domain = domain[0]

            emails = data.get('emails', [])
            emails_str = ", ".join(emails) if isinstance(emails, list) else emails

            info = (
                f"[bold magenta]Domain:[/] {domain}\n"
                f"[bold magenta]Registrar:[/] {data.get('registrar')}\n"
                f"[bold magenta]Organization:[/] {data.get('org')}\n\n"

                f"[bold blue]Country:[/] {data.get('country')} {get_flag(data.get('country'))}\n"
                f"[bold blue]City:[/] {data.get('city')}\n"
                f"[bold blue]State:[/] {data.get('state')}\n\n"

                f"[bold red]Abuse Emails:[/] {emails_str}\n"
                f"[bold red]Whois Server:[/] {data.get('whois_server')}\n\n"

                f"[bold green]Creation date:[/] {data.get('creation_date')}\n"
                f"[bold green]Expiration date:[/] {data.get('expiration_date')}"
            )



        console.print(Panel(info, title=f"[bold cyan]Whois Report for {ip} ({ip_resolved})", subtitle=f"[bold blue]From Cache: [/] {from_cache}"))