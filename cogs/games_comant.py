import discord
from discord.ext import commands
from discord import app_commands
import requests
import random
import asyncio
import io
from PIL import Image, ImageFilter


class PokemonGameCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot,
        self.active_games = {} # Almacenar juegos activos por canal
        
    @app_commands.command(
        name="pokeguess",
        description="🎮 Adivina el Pokémon por la silueta"
    )
    @app_commands.describe(dificultad="Nivel de dificultad")
    @app_commands.choices(
        dificultad = [
            app_commands.Choice(name="Fácil (Gen 1)", value="easy"),
            app_commands.Choice(name="Medio (Gen 1-3)", value="medium"),
            app_commands.Choice(name="Difícil (Todas)", value="hard")
        ]
    )
    async def pokeguess(self, interaction: discord.Interaction, dificultad: str = "medium"):
        # Verificar si ya hay un juego activo en el canal
        if interaction.channel_id in self.active_games:
            await interaction.response.send_message(
                "⚠️ Ya hay un juego activo en este canal. Espera a que termine.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()

        try:
            # Obtener Pokémon aleatorio según dificultad
            pokemon_id = self.get_random_pokemon_id(dificultad)
            pokemon_data = self.get_pokemon_data(pokemon_id)
            
            if not pokemon_data:
                await interaction.followup.send("❌ Error al obtener datos del Pokémon")
                return

            # Crear silueta
            silhouette_image = await self.create_silhouette(pokemon_data["sprites"]["other"]['official-artwork']['front_default'])
            
            if not silhouette_image:
                await interaction.followup.send("❌ Error al crear la silueta")
                return

            # Guardar juego activo
            self.active_games[interaction.channel_id] = {
                "pokemon_id": pokemon_id,
                "pokemon_name": pokemon_data["name"],
                "hints_used": 0,
                "attempts": 0,
                "start_time": discord.utils.utcnow()
            }
            
            # Enviar silueta
            embed = discord.Embed(
                title="🎮 **¿Quién es ese Pokémon?**",
                description="Tienes 3 intentos y 2 pistas disponibles!\nEscribe tu respuesta en el chat.",
                color=0xFFD700
            )
            embed.add_field(
                name="💡 Pistas disponibles",
                value="`/pokedexhint` - Primera letra\n`/typehint` - Tipo del Pokémon",
                inline=False
            )
            embed.add_field(
                name="⏰ Tiempo límite",
                value="2 minutos",
                inline=False
            )
            embed.set_image(url="attachment://silhouette.png")
            embed.set_footer(text="Dificultad: " + dificultad.capitalize())
            
            await interaction.followup.send(
                embed=embed,
                file=discord.File(silhouette_image, filename="silhouette.png")
            )
            
            # Iniciar temporizador
            asyncio.create_task(self.game_timer(interaction.channel_id))
            
        except Exception as e:
            print(f"Error en pokeguess: {e}")
            await interaction.followup.send("❌ Error al iniciar el juego")

    def get_random_pokemon_id(self, difficulty):
        """Obtiene un ID de Pokémon aleatorio según la dificultad"""
        ranges = {
            'easy': (1, 151),    # Gen 1
            'medium': (1, 386),  # Gen 1-3
            'hard': (1, 1025)    # Hasta Gen 9 aprox
        }
        return random.randint(*ranges[difficulty])
    
    def get_pokemon_data(self, pokemon_id):
        """Obtiene datos del Pokémon de la API"""
        try:
            response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{pokemon_id}')
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error en pokeguess: {e}")
    
    async def create_silhouette(self, image_url):
        """Crea una silueta a partir de la imagen del Pokémon"""
        try:
            response = requests.get(image_url)
            if response.status_code != 200:
                return None
            
            # Crear silueta con PIL
            image = Image.open(io.BytesIO(response.content))
            
            # Convertir a escala de grises
            gray_image = image.convert('L')
            # Crear silueta (negro puro)
            # silhouette = gray_image.point(lambda x: 0 if x > 5 else 0)  # Todo negro
            silhouette = gray_image.filter(ImageFilter.GaussianBlur(1))
            
            # Guardar en buffer
            buffer = io.BytesIO()
            silhouette.save(buffer, format='PNG')
            buffer.seek(0)
            
            return buffer
        except Exception as e:
            print(f"Error creando silueta: {e}")
            return None
        
    async def game_timer(self, channel_id):
        """Temporizador para el juego"""
        await asyncio.sleep(120)
        
        if channel_id in self.active_games:
            game = self.active_games[channel_id]
            channel = self.bot.get_channel(channel_id)
            
            if channel:
                embed = discord.Embed(
                title="⏰ **Tiempo agotado!**",
                description=f"El Pokémon era: **{game['pokemon_name'].title()}**",
                color=0xFF0000
            )
            embed.set_image(url=f"https://pokeapi.co/api/v2/pokemon/{game['pokemon_id']}/sprites")
            await channel.send(embed=embed)
        
        del self.active_games[channel_id]
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Escuchar respuestas de los usuarios"""
        if message.author.bot:
            return
        
        if message.channel.id in self.active_games:
            game = self.active_games[message.channel.id]
            user_guess = message.content.lower().strip()
            correct_name = game["pokemon_name"].lower()
            
            game["attempts"] += 1
            
            # Verificar respuesta
            if user_guess == correct_name:
                # ¡Correcto!
                time_taken = (discord.utils.utcnow() - game['start_time']).total_seconds()
                
                embed = discord.Embed(
                    title="🎉 **¡Correcto!**",
                    description=f"**{message.author.mention}** adivinó el Pokémon!",
                    color=0x00FF00
                )
                embed.add_field(
                    name="📊 Estadísticas",
                    value=f"**Pokémon:** {game['pokemon_name'].title()}\n"
                        f"**Intentos:** {game['attempts']}\n"
                        f"**Pistas usadas:** {game['hints_used']}\n"
                        f"**Tiempo:** {time_taken:.1f} segundos",
                    inline=False
                )
                embed.set_image(url=f"https://pokeapi.co/api/v2/pokemon/{game['pokemon_id']}/sprites")
                
                await message.channel.send(embed=embed)
                del self.active_games[message.channel.id]
                
            elif game["attempts"] >= 3:
                # Demasiados intentos
                embed = discord.Embed(
                    title="❌ **Demasiados intentos**",
                    description=f"El Pokémon era: **{game['pokemon_name'].title()}**",
                    color=0xFF0000
                )
                embed.set_image(url=f"https://pokeapi.co/api/v2/pokemon/{game['pokemon_id']}/sprites")
                await message.channel.send(embed=embed)
                del self.active_games[message.channel.id]
                    
    @app_commands.command(
        name="pokedexhint",
        description="💡 Obtén una pista (primera letra)"
    )
    async def pokedex_hint(self, interaction: discord.Interaction):
        """Da la primera letra del Pokémon"""
        if interaction.channel_id not in self.active_games:
            await interaction.response.send_message(
                "❌ No hay ningún juego activo en este canal",
                ephemeral=True
            )
            return

        game = self.active_games[interaction.channel_id]
        
        if game["hints_used"] >= 2:
            await interaction.response.send_message(
                "❌ Ya usaste todas las pistas disponibles",
                ephemeral=True
            )
            return
        
        game['hints_used'] += 1
        first_letter = game['pokemon_name'][0].upper()
        
        await interaction.response.send_message(
            f"💡 **Pista:** La primera letra es **{first_letter}**",
            ephemeral=True
        )

    @app_commands.command(
        name="typehint",
        description="💡 Obtén una pista (tipo del Pokémon)"
    )
    async def type_hint(self, interaction: discord.Interaction):
        """Da el tipo del Pokémon"""
        if interaction.channel_id not in self.active_games:
            await interaction.response.send_message(
                "❌ No hay ningún juego activo en este canal",
                ephemeral=True
            )
            return
        
        game = self.active_games[interaction.channel_id]
        
        if game["hints_used"] >= 2:
            await interaction.response.send_message(
                "❌ Ya usaste todas las pistas disponibles",
                ephemeral=True
            )
            return
        
        pokemon_data = self.get_pokemon_data(game["pokemon_id"])
        if not pokemon_data:
            await interaction.response.send_message(
                "❌ Error al obtener la pista",
                ephemeral=True
            )
            return

        types = [t["type"]["name"].title() for t in pokemon_data["types"]]
        game["hints_used"] += 1
        
        await interaction.response.send_message(
            f"💡 **Pista:** El tipo es **{'/' .join(types)}**",
            ephemeral=True
        )
    
    @app_commands.command(
        name="giveup",
        description="🏳️ Rendirse y revelar el Pokémon"
    )
    async def give_up(self, interaction: discord.Interaction):
        """Revela el Pokémon actual"""
        if interaction.channel_id not in self.active_games:
            await interaction.response.send_message(
                "❌ No hay ningún juego activo en este canal",
                ephemeral=True
            )
            return
        
        game = self.active_games[interaction.channel_id]
        
        embed = discord.Embed(
            title="🏳️ **Te has rendido**",
            description=f"El Pokémon era: **{game['pokemon_name'].title()}**",
            color=0xFFA500
        )
        embed.set_image(url=f"https://pokeapi.co/api/v2/pokemon/{game['pokemon_id']}/sprites")
        
        await interaction.response.send_message(embed=embed)
        del self.active_games[interaction.channel.id]

async def setup(bot):
    await bot.add_cog(PokemonGameCog(bot))
