import subprocess
import os 
from scraper import CTFdScraper
import yaml

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

CHALL_DIR = config['chall_dir']
FLAG_FORMAT = config['ctf']['flag_format']
URL = config['scraping']['url']

scraper = CTFdScraper(url=URL, headless=config['scraping']['headless'], login=config['scraping']['login'], user=config['scraping']['user'], password=config['scraping']['password'])

# create chall dir if chall dir doesn't exist
os.makedirs(CHALL_DIR, exist_ok=True)

challenges = scraper.scrape_ctfd()

flags = []
for chall in challenges: 
    chall_dir = os.path.join(CHALL_DIR, chall['name'])
    os.makedirs(chall_dir, exist_ok=True)
    for f in chall['files']:
        subprocess.run(
            ["wget", f["url"]],
            cwd=chall_dir,
            check=False
            )   

    print(f"Downloaded all {len(chall['files'])} files!")

    prompt = f"""
    You are an expert Capture The Flag (CTF) player.
    You are given one challenge with the following information:
    Challenge Name: {chall['name']},
    Challenge Description: {chall['description']}
    All files required to solve the challenge are in the current working directory.
    You may inspect and reason about these files as required. 

    Task: 
    Determine the correct flag for this challenge. 

    Output rules:
    - Output ONLY the flag 
    - The flag format is exactly {FLAG_FORMAT}{{...}}, unless otherwise stated in the challenge description
    - Do NOT include explanation, reasoning or other text
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
        print(result.stdout)
        flag = result.stdout.strip()
        if flag is not None:
            scraper.submit_flag(chall['name'], flag)
    
    except:
        print("Codex failed to run. Check if codex is installed: https://openai.com/codex/.")