import requests
import discord
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
                await ctx.send(image_url)

        except Exception as e:
            print("Error: ", e)

    @commands.command(name="poked-info")
    @commands.has_permissions(administrator=True)
    async def poked_info(self, ctx, args):
        try:
            # Obtener datos de la PokeAPI
            pokemon = args.split(" ",1)[0].lower()
            response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon}")
            
            if response.status_code != 200:
                await ctx.send("Informacion del pokemon no encontrada")
                return
            
            data = response.json()
            
            # Obtener datos de especie para la descripción
            species_responce = requests.get(data["species"]["url"])
            species_data = species_responce.json()
            
            # Crear embed bonito
            embed = discord.Embed(
                title=f"#{data["id"]:03d} - {data["name"].title()}",
                color=self.get_color(data["types"][0]["types"]["name"]),
                description=self.get_description(species_data)
            )
            
            # Imagen del Pokémon
            embed.set_thumbnail(url=data["sprites"]["other"]['official-artwork']['front_default'])
            
            # Tipos
            types = " | ".join([t["type"]["name"].title() for t in data["types"]])
            embed.add_field(name="🔮 **Tipos**", value=types, inline=False)
            
            # Stats principales
            stats = self.format_stats(data["stats"])
            embed.add_field(name="⚡ **Estadísticas**", value=stats, inline=False)
            
            # Altura y Peso
            embed.add_field(
                name="📏 **Características**",
                value=f"**Altura:** {data['height'] / 10:.1f}m\n**Peso:** {data['weight'] / 10:.1f}kg",
                inline=True
            )
            
            # Habilidades
            abilities = ", ".join([a['ability']['name'].title() for a in data['abilities']])
            embed.add_field(name="✨ **Habilidades**", value=abilities, inline=True)
            
            # Footer con datos adicionales
            embed.set_footer(text=f"💕 Experiencia base: {data['base_experience']} | 🎮 Generación: {self.get_generation(species_data)}")
            
            await ctx.send(embed=embed)
                
        except Exception as e:
            print("Error: ", e)
    
    @poked.error
    async def error_type(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send("tienes que pasar un pokemon")
            
async def setup(bot):
    await bot.add_cog(PokedexComant(bot))
