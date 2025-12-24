from playwright.sync_api import sync_playwright

def scrape_ctfd(url, headless=True, login=True, user="techie", password="ernie"):
    challenges = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        if login:
            page.goto(f"{url}/login", timeout=60000)
            page.fill('input[name="name"]', user)
            page.fill('input[name="password"]', password)
            page.click('input[type="submit"]')
            print("login successful")

        page.goto(f"{url}/challenges", timeout=60000)
        page.wait_for_selector('.challenge-button')
        challenge_buttons = page.locator('.challenge-button')
        count = challenge_buttons.count() # number of challs
        
        for i in range(count):
            page.locator(".challenge-button").nth(i).click() # open chall
            modal = page.locator("#challenge-window")
            modal.wait_for(state="visible")

            name = page.locator(".challenge-name").inner_text().strip()
            description = page.locator(".challenge-desc").inner_text().strip()
            points = page.locator(".challenge-value").inner_text().strip()
            files = []
            for f in page.locator(".challenge-files a").all():
                files.append({
                    "name": f.inner_text().strip(),
                    "url": f"{url}{f.get_attribute("href")}"
                })
            
            modal = page.locator("#challenge-window")
            modal.wait_for(state="visible")
            modal.locator("button.btn-close").click()
            modal.wait_for(state="hidden")
            challenge = {}
            challenge['name'] = name
            challenge['description'] = description
            challenge['files'] = files
            challenge['points'] = points
            challenges.append(challenge)
            
        browser.close()
        return challenges

# TODO: Add auto-submission of flags

if __name__ == "__main__":
    print(scrape_ctfd())