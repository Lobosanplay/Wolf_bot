from discord.ext import commands
from discord import app_commands
import discord
import asyncio


class Comand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="repit",
        description="repite lo que le pases"
    )
    @app_commands.describe(repite="Pon lo que quieras q el bot repita")
    async def repit(self, interaction: discord.Interaction, repite: str):
        await interaction.response.send_message(repite)
        
    @app_commands.command(
        name="clear",
        description="Limpia todos los mensajes del canal (máx 1000 mensajes)"
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Contador de mensajes borrados
            total_deleted = 0
            
            # Borrar mensajes en lotes de 100 (máximo por llamada)
            while True:
                # Borrar hasta 100 mensajes a la vez
                deleted = await interaction.channel.purge(limit=100)
                deleted_count = len(deleted)
                total_deleted += deleted_count
                
                # Si borró menos de 100, significa que no hay más mensajes
                if deleted_count < 100:
                    break
                
                # Pequeña pausa para evitar rate limits
                await asyncio.sleep(1)
            
            if total_deleted == 0:
                await interaction.followup.send(
                    "❌ No hay mensajes para borrar o no tengo permisos",
                    ephemeral=True
                )
                return
            
            # Enviar confirmación
            await interaction.followup.send(
                f"✅ Se borraron {total_deleted} mensajes del canal", 
                ephemeral=True
            )
            
            # Enviar mensaje al canal (se autoborrará)
            msg = await interaction.channel.send(
                f"🗑️ Se borraron {total_deleted} mensajes del canal", 
                delete_after=5
            )
            
        except discord.Forbidden:
            await interaction.followup.send(
                "❌ No tengo permisos para borrar mensajes en este canal",
                ephemeral=True
            )
        except discord.HTTPException as e:
            await interaction.followup.send(
                f"❌ Error al borrar mensajes: {e}",
                ephemeral=True
            )

    @clear.error
    async def clear_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ Necesitas permisos de **Gestionar Mensajes** para usar este comando",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(Comand(bot))