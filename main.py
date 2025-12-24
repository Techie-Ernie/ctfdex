import subprocess
import os 
from scraper import scrape_ctfd

url = "http://127.0.0.1:4000"

challenges = scrape_ctfd(url)
BASE_DIR = os.getcwd()
FLAG_FORMAT = 'picoCTF'

flags = []
for chall in challenges: 
    chall_dir = os.path.join(BASE_DIR, chall['name'])
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
        flags.append(result.stdout.strip())
        print(flags)
    except:
        print("Codex failed to run. Check if codex is installed: https://openai.com/codex/.")