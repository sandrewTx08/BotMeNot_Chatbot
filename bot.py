from lxml.etree import HTML
from urllib.request import Request, urlopen
from discord import Client
from datetime import datetime

client = Client()


@client.event
async def on_message(message):
    class Locators:
        """ Location for elements path in the page """

        """ Exception locations """
        NOT_FOUND = "//*[text()='No logins found. Please register a fake account then ']"
        DENIED = "//*[text()='This site has been barred from the bugmenot system.']"

        """ Target locations """
        USERNAME = '//*[@class="account"]/dl/dd[1]'
        PASSWORD = '//*[@class="account"]/dl/dd[2]'
        SUCCESS_RATE = '//*[@class="account"]/dl/dd[@class="stats"]/ul/li[@class]'
        VOTES = '//*[@class="account"]/dl/dd[@class="stats"]/ul/li[2]'
        LOGIN_AGE = '//*[@class="account"]/dl/dd[@class="stats"]/ul/li[3]'

    class Scraper:
        """ BugMeNot_ScraperV2 """

        def __init__(self, url):
            """ Search shared login based on <url> instance argument """
            self.url = url
            self.begin_time = datetime.now()
            self.body = HTML(
                urlopen(
                    Request(
                        url=f'http://bugmenot.com/view/{url}',
                        headers={
                            'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}
                    )
                ).read()
            )
            self.frame = self.frame()
            self.finished_time = datetime.now() - self.begin_time

        """ Returns all share login information:
        Username, Password, Success rate, Votes and Login age.
        """

        def username(self):
            """ Return values """
            for _ in self.body.xpath(Locators.USERNAME):
                yield _.xpath('string()')

        def password(self):
            """ Return values """
            for _ in self.body.xpath(Locators.PASSWORD):
                yield _.xpath('string()')

        def success_rate(self):
            """ Return values """
            for _ in self.body.xpath(Locators.SUCCESS_RATE):
                yield _.xpath('string()')

        def votes(self):
            """ Return values """
            for _ in self.body.xpath(Locators.VOTES):
                yield _.xpath('string()')

        def login_age(self):
            """ Return values """
            for _ in self.body.xpath(Locators.LOGIN_AGE):
                yield _.xpath('string()')

        def frame(self):
            """ Base to build formatters """
            if self.body.xpath(Locators.DENIED) or self.body.xpath(Locators.NOT_FOUND):
                """ Check for invalid results """
                raise Exception(f'Search <{self.url}> looks invalid, please try something else.')

            else:
                def username():
                    return [_ for _ in self.username()]

                def password():
                    return [_ for _ in self.password()]

                def success_rate():
                    return [_.replace(' ', '')
                                .replace('successrate', '')
                            for _ in self.success_rate()]

                def votes():
                    return [_.replace(' ', '')
                                .replace('votes', '')
                            for _ in self.votes()]

                def login_age():
                    return [_.replace(' ', '')
                                .replace('years', 'Y')
                                .replace('months', 'M')
                                .replace('days', 'D')
                                .replace('hours', 'H')
                                .replace('old', '')
                            for _ in self.login_age()]

                return [
                    username(),
                    password(),
                    success_rate(),
                    votes(),
                    login_age()
                ]

        def display(self, limit):
            """ Message to be send """
            text = f"""```yaml
🔧 Version: BugMeNot_ScraperV2
🌐 Site: https://bugmenot.com/view/{self.url}
📄 Total Results: {len(self.frame[0])}
🕗 Response time: {self.finished_time}
```"""
            if len(self.frame[0]) < limit:
                limit = len(self.frame[0])

            for _ in range(limit):
                text += f"""```yaml
👤 Username: {self.frame[0][_]}
🔑 Password: {self.frame[1][_]}
📊 Success Rate: {self.frame[2][_]}
🥇 Votes: {self.frame[3][_]}
🕗 Login Age: {self.frame[4][_]}
```"""
            return text

    """ Trigger bot when '!' is send on chat """
    if message.content.startswith('!'):
        await message.channel.send(
            Scraper(
                message.content
                .replace('!', '')
            ).display(3)
        )

client.run('')