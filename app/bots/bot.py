from app.bots.base_bot import BaseBot
import asyncio

class Bot1(BaseBot):
    def __init__(self):
        super().__init__("BOT_TOKEN")

async def main():
    bot = Bot1()
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())