# message_parser.py
import asyncio


class MessageParser():
    def __init__(self, fab):
        self.fab = fab

    async def parse_command(self, message):
        if message.content == "test":
            await self.__parse_test(message)
        return

    async def __parse_test(self, message):
        await self.fab.send_message(message.channel, "Testing 1 2 3!")
