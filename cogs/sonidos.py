import discord
from discord.ext import commands
from discord import app_commands
import requests
import io

class SonidosPokemon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="voice-pokemon",
        description="Envía y reproduce el sonido del Pokémon"
    )
    @app_commands.describe(pokemon="Pokemon a buscar")
    async def VoicePokemon(self, interaction: discord.Interaction, pokemon: str):
        await interaction.response.defer()
        
        try:
            # Obtener datos del Pokémon
            result = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon.lower()}")
            if result.status_code != 200:
                await interaction.followup.send("❌ Pokémon no encontrado")
                return

            data = result.json()
            voice_url = data["cries"]["legacy"]
            
            # Descargar el audio
            audio_response = requests.get(voice_url)
            if audio_response.status_code != 200:
                await interaction.followup.send("❌ Error al descargar el audio")
                return
            
            # Crear archivo de audio para enviar
            audio_file = discord.File(
                io.BytesIO(audio_response.content),
                filename=f"{data['name']}_cry.ogg"  # Los sonidos de Pokémon suelen ser .ogg
            )
            
            # Enviar embed con el archivo de audio
            embed = discord.Embed(
                title=f"🔊 {data['name'].title()}",
                color=self.get_color(data["types"][0]["type"]["name"]),
                description=f"Sonido de {data['name'].title()}"
            )
            
            # Enviar mensaje con el audio
            await interaction.followup.send(embed=embed, file=audio_file)
            
        except Exception as e:
            print("Error: ", e)
            await interaction.followup.send("❌ Error al obtener el sonido del Pokémon")
    
    @app_commands.command(
        name="get-pokemon-sound",
        description="Obtiene solo el archivo de audio del Pokémon"
    )
    @app_commands.describe(pokemon="Pokemon a buscar")
    async def GetPokemonSound(self, interaction: discord.Interaction, pokemon: str):
        """Solo envía el archivo de audio sin reproducir"""
        await interaction.response.defer()
        
        try:
            # Obtener datos del Pokémon
            result = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon.lower()}")
            if result.status_code != 200:
                await interaction.followup.send("❌ Pokémon no encontrado")
                return

            data = result.json()
            voice_url = data["cries"]["legacy"]
            
            # Descargar el audio
            audio_response = requests.get(voice_url)
            if audio_response.status_code != 200:
                await interaction.followup.send("❌ Error al descargar el audio")
                return
            
            # Crear archivo de audio
            audio_file = discord.File(
                io.BytesIO(audio_response.content),
                filename=f"{data['name']}_cry.ogg"
            )
            
            # Enviar solo el archivo
            await interaction.followup.send(
                content=f"🎵 Sonido de {data['name'].title()}",
                file=audio_file
            )
            
        except Exception as e:
            print("Error: ", e)
            await interaction.followup.send("❌ Error al obtener el sonido del Pokémon")
    
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
    
async def setup(bot):
    await bot.add_cog(SonidosPokemon(bot))