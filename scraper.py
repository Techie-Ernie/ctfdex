from playwright.sync_api import sync_playwright
import time 

class CTFdScraper():
    def __init__(self, url, headless, login, user, password):
        self.url = url
        self.headless = headless
        self.login = login
        self.user = user
        self.password = password

    def scrape_ctfd(self):
        challenges = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page()

            if self.login:
                page.goto(f"{self.url}/login", timeout=60000)
                page.fill('input[name="name"]', self.user)
                page.fill('input[name="password"]', self.password)
                page.click('input[type="submit"]')
                print("Login successful")

            page.goto(f"{self.url}/challenges", timeout=60000)
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
                        "url": f"{self.url}{f.get_attribute("href")}"
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

    def submit_flag(self, chall_name, flag):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page()
            if self.login:
                page.goto(f"{self.url}/login", timeout=60000)
                page.fill('input[name="name"]', self.user)
                page.fill('input[name="password"]', self.password)
                page.click('input[type="submit"]')
                print("Login successful")

            page.goto(f"{self.url}/challenges", timeout=60000)
            page.wait_for_selector('.challenge-button')
            challenge_button = page.locator('.challenge-button', has_text=chall_name)     
            challenge_button.first.click()       
            modal = page.locator("#challenge-window")
            modal.wait_for(state="visible")
            
            modal.locator('input[name="submission"]').fill(flag) # fill in with flag
            modal.locator('#challenge-submit').click() # submit 
            time.sleep(1) # short pause for submission to go through 
            browser.close()

