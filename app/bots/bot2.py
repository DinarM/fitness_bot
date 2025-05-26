import asyncio
from app.bots.base_bot import BaseBot

class Bot2(BaseBot):
    def __init__(self):
        super().__init__("BOT_TOKEN2")

async def main():
    bot = Bot2()
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())