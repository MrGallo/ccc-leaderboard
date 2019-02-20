import os
import requests


class CCCScraper:
    def __init__(self, username: str, password: str, dev_mode: bool = False):
        self.username = username
        self.password = password
        self.dev_mode = dev_mode
        self.session = None

        if not self.dev_mode:
            self.login()

    def login(self):
        login_url = 'https://cccgrader.com/teachers/login.php'
        login_info = {'username': self.username, 'password': self.password}

        self.session = requests.Session()
        self.session.post(login_url, data=login_info)

    def scrape_leaderboard_html(self, contest_id: int) -> str:
        if not self.dev_mode:
            # print("fetching production")
            html = self.session.get(f"https://cccgrader.com/teachers/scoreboard.php?contestid={contest_id}").content
        else:
            dev_filename = f"leaderboard{contest_id}.txt"
            if os.path.exists(dev_filename):
                with open(dev_filename, 'r') as f:
                    html = f.read()
            else:
                self.login()
                with open(dev_filename, 'w') as f:
                    print(f"fetching into {dev_filename}")
                    html = self.session.get(
                        f"https://cccgrader.com/teachers/scoreboard.php?contestid={contest_id}").content
                    f.write(str(html))

        return str(html)
