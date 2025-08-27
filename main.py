import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("TOKEN")
id = os.getenv("ID")
# Configurar intents con Slash Commands
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Usar commands.Bot con intents
bot = commands.Bot(
    command_prefix='/',  
    intents=intents,
    help_command=None
    )

async def load_cogs():
    try:
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py") and filename != "__init__.py":
                await bot.load_extension(f"cogs.{filename[:-3]}")
        print("✅ Cogs cargados correctamente")
        print(f"Invita al bot con este comando: \n https://discord.com/oauth2/authorize?client_id={id}&permissions=8&integration_type=0&scope=applications.commands+bot")
    except Exception as e:
        print(e)

@bot.event
async def on_ready():
    print(f'✅ {bot.user} ha iniciado sesión!')
    
    # Sincronizar Slash Commands
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} Slash Commands sincronizados")
    except Exception as e:
        print(e)

async def main():
    async with bot:
        await load_cogs()
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
