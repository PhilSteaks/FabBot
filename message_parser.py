# message_parser.py
import asyncio


class MessageParser():
    def __init__(self, fab):
        self.fab = fab

    async def parse_command(self, message):
        if message.content == "test":
            await self.__parse_test(message)
        if "years ago" in message.content.lower():
            await self.__parse_years_ago(message)
        return

    async def __parse_test(self, message):
        await self.fab.send_message(message.channel, "Testing 1 2 3!")

    async def __parse_years_ago(self, message):
        await self.fab.send_message(
            message.channel, "https://www.youtube.com/watch?v=r_WWkQgT3To")
