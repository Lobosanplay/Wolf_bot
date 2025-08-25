import requests
import discord
from discord import app_commands
from discord.ext import commands

class PokedexComant(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  # <-- Quita la coma aquí
        
    @app_commands.command(
        name="poked",
        description="Muestra una imagen de un Pokémon"
    )
    @app_commands.describe(pokemon="Nombre del Pokémon a buscar")
    async def poked(self, interaction: discord.Interaction, pokemon: str):  # <-- Corrección aquí
        await interaction.response.defer()
        
        try:
            result = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon.lower()}")
            
            if result.status_code != 200:  # <-- Mejor forma de verificar
                await interaction.followup.send("❌ Pokémon no encontrado")
            else:
                data = result.json()
                image_url = data["sprites"]["other"]["official-artwork"]["front_default"] or data["sprites"]["front_default"]
                embed = discord.Embed(
                    title=f"{data['name'].title()}",
                    color=0x00FF00
                )
                embed.set_image(url=image_url)
                await interaction.followup.send(embed=embed)

        except Exception as e:
            print("Error: ", e)
            await interaction.followup.send("❌ Error al buscar el Pokémon")

    @app_commands.command(
        name="poked_info",
        description="Muestra información detallada de un Pokémon"
    )
    @app_commands.describe(pokemon="Nombre del Pokémon a buscar")
    async def poked_info(self, interaction: discord.Interaction, pokemon: str):  # <-- Corrección aquí
        await interaction.response.defer()
        
        try:
            # Obtener datos de la PokeAPI
            response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon.lower()}")
            
            if response.status_code != 200:
                embed = discord.Embed(
                    title="❌ Pokémon no encontrado",
                    description=f"No se encontró el Pokémon: **{pokemon}**",
                    color=0xFF0000
                )
                embed.add_field(
                    name="💡 Sugerencias",
                    value="• Revisa la ortografía\n• Usa el nombre en inglés\n• Prueba con el número de la Pokédex",
                    inline=False
                )
                await interaction.followup.send(embed=embed)
                return

            data = response.json()
            
            # Obtener datos de especie para la descripción
            species_response = requests.get(data["species"]["url"])
            species_data = species_response.json()
            
            # Crear embed bonito
            embed = discord.Embed(
                title=f"#{data['id']:03d} - {data['name'].title()}",
                color=self.get_color(data["types"][0]["type"]["name"]),
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
            
            await interaction.followup.send(embed=embed)
                
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Error del servidor",
                description="No se pudo obtener la información del Pokémon. Intenta nuevamente.",
                color=0xFF0000
            )
            await interaction.followup.send(embed=error_embed)
            print(f"Error: {e}")
    
    def get_color(self, type_name):
        """Asigna colores según el tipo del Pokémon"""
        colors = {
            'normal': 0xA8A878, 'fire': 0xF08030, 'water': 0x6890F0,
            'electric': 0xF8D030, 'grass': 0x78C850, 'ice': 0x98D8D8,
            'fighting': 0xC03028, 'poison': 0xA040A0, 'ground': 0xE0C068,
            'flying': 0xA890F0, 'psychic': 0xF85888, 'bug': 0xA8B820,
            'rock': 0xB8A038, 'ghost': 0x705898, 'dragon': 0x7038F8,
            'dark': 0x705848, 'steel': 0xB8B8D0, 'fairy': 0xEE99AC
        }
        return colors.get(type_name, 0x000000)

    def format_stats(self, stats):
        """Formatea las estadísticas de forma legible"""
        stat_names = {
            'hp': '❤️ HP', 'attack': '⚔️ Ataque', 
            'defense': '🛡️ Defensa', 'special-attack': '🔮 Ataque Especial',
            'special-defense': '✨ Defensa Especial', 'speed': '⚡ Velocidad'
        }
        
        return "\n".join([
            f"{stat_names[stat['stat']['name']]}: **{stat['base_stat']}**"
            for stat in stats
        ])

    def get_description(self, species_data):
        """Obtiene la descripción en español"""
        for entry in species_data['flavor_text_entries']:
            if entry['language']['name'] == 'es':
                return entry['flavor_text'].replace('\n', ' ').replace('\f', ' ')
        return "Descripción no disponible en español."

    def get_generation(self, species_data):
        """Obtiene la generación del Pokémon"""
        gen_url = species_data['generation']['url']
        gen_number = gen_url.split('/')[-2]
        return f"Gen {gen_number}"
            
async def setup(bot):
    await bot.add_cog(PokedexComant(bot))