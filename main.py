from bs4 import BeautifulSoup
import requests, os, threading, re, tls_client, ctypes
from colorama import init, Fore, Style

proxies = {"http": ""} # Proxy here
session = tls_client.Session(client_identifier="chrome112")
def get_server_redirect_url(keyword, catergory, page, url_set):
    success = 0
    failed = 0
    if len(keyword.split()) > 1:
        keyword = keyword.replace(" ", "+")
    try:
        r = session.get(f'https://discadia.com/?q={keyword}&sort={catergory}&page={page}').text
        soup = BeautifulSoup(r, 'html.parser')
        servers = soup.findAll('a', class_="server-join-button")
        for server in servers:
            server_href = server.get('href')
            url = f"https://discadia.com/{server_href}"
            x = session.get(url, proxy=proxies)
            soup = BeautifulSoup(x.text, 'html.parser')
            meta_tag = soup.find('meta', {'http-equiv': 'refresh'})
            if meta_tag:
                redirect_url = meta_tag['content'].split('; url=')[1]
                invite_code = re.search(r'invite/(.+)', redirect_url).group(1)
                url_set.add(invite_code)
                r = session.get(f'https://discord.com/api/v10/invites/{invite_code}', proxy=proxies).json()
                guild_name = r['guild']['name']
                verification_level = str(r['guild']['verification_level'])
                boost_level = str(r['guild']['premium_subscription_count'])
                print("[" + Fore.GREEN + "SCRAPED" +  Style.RESET_ALL + "] " +  f"Guild name: " + Fore.LIGHTYELLOW_EX + guild_name + Style.RESET_ALL + " | Verification: " + Fore.LIGHTYELLOW_EX + verification_level + Style.RESET_ALL + " | Boosts: " + Fore.LIGHTYELLOW_EX + boost_level + Style.RESET_ALL)
                success += 1
            else:
                print("[" + Fore.RED + "FAILED" +  Style.RESET_ALL + "] " +  f"Failed to scrape due to connection issues")
                failed += 1
    except:
        print("[" + Fore.RED + "FAILED" +  Style.RESET_ALL + "] " +  f"Failed to scrape due to connection issues")
    ctypes.windll.kernel32.SetConsoleTitleW(f"Success: {success} | Failed: {failed}")

def discardia(keyword, categories):
    pages = int(input("\nNumber of pages to scrape (recommended 5-10)\n> "))
    os.system('cls')
    threads = []
    url_set = set()
    print(f">>> CATEGORY: TOP, NEW, ACTIVE | PAGES: {pages} <<<")
    for catergory in categories:
        for i in range(pages):
            thread = threading.Thread(target=get_server_redirect_url, args=(keyword, catergory, i, url_set))
            threads.append(thread)
            thread.start()

    for thread in threads:
        thread.join()

    try:
        with open('invites.txt', 'r') as file:
            existing_codes = set(line.strip() for line in file)
    except FileNotFoundError:
        existing_codes = set()

    all_codes = existing_codes.union(url_set)

    with open('invites.txt', 'w') as file:
        for code in all_codes:
            file.write(f"discord.gg/{code}\n")

keyword = input("\nKeyword to lookup Discord servers\n> ")
categories = ["top", "new", "active"]

discardia(keyword, categories)
