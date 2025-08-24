import requests
from discord.ext import commands


class PokedexComant(commands.Cog):
    def __init__(self, bot):
        self.bot = bot,
        
    @commands.command(name="poked")
    @commands.has_permissions(administrator=True)
    async def poked(self, ctx, args):
        try:
            pokemon = args.split(" ",1)[0].lower()
            result = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon}")
            
            if result.text == "Not Found":
                await ctx.send("Pokemon no Encontrado")
            else:
                image_url = result.json()["sprites"]["front_default"]
                print(image_url)
                await ctx.send(image_url)

        except Exception as e:
            print("Error: ", e)

    @poked.error
    async def error_type(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send("tienes que pasar un pokemon")
            
async def setup(bot):
    await bot.add_cog(PokedexComant(bot))
