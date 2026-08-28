from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from icmplib import ping, traceroute
from icmplib.exceptions import ICMPLibError
from iprad.utils.functions import get_flag, get_resolved_ip

#IPinfo module
class PingTracertClient:
    def check_ip(self, ip: str):

        #resolve ip 
        ip_resolved = get_resolved_ip(ip)
        
        console = Console()
        # console.clear()
        
        #Pinging
        with console.status("[bold green]Pinging...") as status:

            data = {
                "alive": None,
                "latency_avg": None,
                "loss": None,
                "latency_min": None
            }
            
            try:
                host = ping(ip_resolved, count=3, timeout=1)
                if host.is_alive:
                    data["latency_avg"] = f"{host.avg_rtt} ms"
                    data["latency_min"] = f"{host.min_rtt} ms"
                    data["latency_max"] = f"{host.max_rtt} ms"
                    data['loss'] = f"{host.packet_loss * 100}%"
                    data['alive'] = host.is_alive
                else:
                    data["alive"] = "False ❌"
            except PermissionError:
                console.print("[bold red]Permission error! Run with sudo or administrator rights")
                return
            except ICMPLibError as e:
                console.print(f"[bold red]Error! {e}")
                return

            info = (
                f"[bold green]Alive:[/] {data.get('alive')}\n"
                f"[bold green]Average Latency:[/] {data.get('latency_avg')}\n"
                f"[bold green]Loss:[/] {data.get('loss')}\n\n"

                f"[bold purple]Min latency:[/] {data.get('latency_min')}\n"
                f"[bold purple]Max latency:[/] {data.get('latency_max')}"
            )



        console.print(Panel(info, title=f"[bold cyan]Ping Report for {ip} ({ip_resolved})"))

        with console.status("[bold green]Traceroute in progress (it can take 20-60 seconds)") as status:
            try:
                hops = traceroute(
                    ip_resolved, 
                    count=2,      
                    timeout=4,
                    max_hops=20   
                )

            except ICMPLibError as e:
                console.print(f"[bold red]Error! {e}")
                return

            table = Table(title_style="bold magenta", show_lines=True)
            table.add_column("№", justify="right", style="dim")
            table.add_column("IP", style="cyan")
            table.add_column("RTT", justify="right")


            for hop in hops:
                h_ip = hop.address if hop.address else "[red]* * *"

                table.add_row(str(hop.distance), h_ip, f"{hop.avg_rtt} ms")

        
        console.print(Panel(table, title=f"[bold cyan]Fast traceroute report for {ip} ({ip_resolved})",))