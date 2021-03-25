# main.py
from fab_bot import FabBot

k_bot_token = "<Insert Token>"

if __name__ == "__main__":
    print("Starting Bot...")
    bot = FabBot()
    bot.run(k_bot_token)
    print("Stopped Bot")
