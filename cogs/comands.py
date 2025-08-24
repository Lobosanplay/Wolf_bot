from discord.ext import commands

class Comand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="repit")
    @commands.has_permissions(manage_messages=True)
    async def test(self, ctx, *args):
        respuestas = " ".join(args)
        await ctx.send(respuestas)

    @commands.command(name="clear")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx):
        await ctx.channel.purge()
        await ctx.send("Todo limpio", delete_after=3)
        
async def setup(bot):
    await bot.add_cog(Comand(bot))
