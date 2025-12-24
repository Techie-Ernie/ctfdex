# CTFDex

> [!IMPORTANT]
> Don't rely on this tool to solve CTF challenges for you if you're serious about learning cybersecurity. This is just an experiment :)

### What this does 
CTFDex can scrape [CTFd](https://ctfd.io/)-based CTF sites for challenges using [playwright](https://playwright.dev/python/docs/intro), and extracts challenge titles, descriptions, points and any challenge files. 

Each challenge is then passed into OpenAI's Codex which attempts to solve the challenge and return the flag. 

### Installation

Install Python, git and [Codex](https://openai.com/codex/)

```bash
git clone https://github.com/Techie-Ernie/ctfdex.git
cd ctfdex
pip install -r requirements.txt
playwright install 
python main.py 
