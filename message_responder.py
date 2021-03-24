import asyncio

async def do_nothing():
    pass

class MessageResponder():
    def __init__(self, fab):
        self.fab = fab

    def parse_command(self, message):
        if message.content == "test":
            return self.__parse_test(message)
        if "years ago" in message.content.lower():
            return self.__parse_years_ago(self, message)
        return do_nothing()

    def __parse_test(self, message):
        return self.fab.send_message(message.channel, "Testing 1 2 3!")

    def __parse_years_ago(self, message):
        return self.fab.send_message(message.channel, "https://www.youtube.com/watch?v=r_WWkQgT3To")

