import subprocess
import os 
from scraper import CTFdScraper
import yaml
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

parser = argparse.ArgumentParser(prog="CTFDex", description="CTF Solver with Codex")
parser.add_argument("--config", '-c', default='config.yaml')
args = parser.parse_args()

with open(args.config, 'r') as f:
    config = yaml.safe_load(f)

CHALL_DIR = config['chall_dir']
FLAG_FORMAT = config['ctf']['flag_format']
URL = config['scraping']['url']

scraper = CTFdScraper(url=URL, headless=config['scraping']['headless'], login=config['scraping']['login'], user=config['scraping']['user'], password=config['scraping']['password'])

# create chall dir if chall dir doesn't exist
os.makedirs(CHALL_DIR, exist_ok=True)

challenges = scraper.scrape_ctfd()


def solve_and_submit(chall):
    chall_dir = os.path.join(CHALL_DIR, chall['name'])
    os.makedirs(chall_dir, exist_ok=True)

    for f in chall['files']:
        if os.name == 'nt':
            subprocess.run(
                ["curl", "-LO", f["url"]],
                cwd=chall_dir,
                check=False,
            )
        else:
            subprocess.run(
                ["wget", f["url"]],
                cwd=chall_dir,
                check=False
            )

    print(f"Downloaded {len(chall['files'])} files for {chall['name']}")

    prompt = f"""
    You are an expert Capture The Flag (CTF) player.
    You are given one challenge with the following information:
    Challenge Name: {chall['name']}
    Challenge Description: {chall['description']}

    All files required to solve the challenge are in the current working directory.

    Task:
    Determine the correct flag for this challenge.

    Output rules:
    - Output ONLY the flag
    - The flag format is exactly {FLAG_FORMAT}{{...}}, unless otherwise stated
    - If the flag cannot be determined, output {FLAG_FORMAT}{{unknown}}
    """

    try:
        result = subprocess.run(
            ["codex", "exec", "-", "--skip-git-repo-check"],
            input=prompt,
            text=True,
            capture_output=True,
            cwd=chall_dir,
            check=False,
        )

        flag = result.stdout.strip()
        print(f"{chall['name']}:{flag}")
        if flag:
            if flag == FLAG_FORMAT + "{unknown}":
                print(f"Codex failed  to solve {chall['name']}")
            else:
                scraper.submit_flag(chall['name'], flag)

    except Exception as e:
        print(f"Codex failed for {chall['name']}: {e}")

MAX_WORKERS = min(8, os.cpu_count()) 

with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = [executor.submit(solve_and_submit, chall) for chall in challenges]

    for future in as_completed(futures):
        try:
            future.result()
        except Exception as e:
            print(f"[!] Worker error: {e}")
