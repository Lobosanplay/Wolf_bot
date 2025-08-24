import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

token = os.getenv("TOKEN")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix = "/", intents=intents)

@bot.event
async def on_ready():
    print(f"running {bot.user}")

async def load_cog():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and filename != "__init__.py":
            await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    async with bot:
        await load_cog()
        await bot.start(token)

asyncio.run(main())