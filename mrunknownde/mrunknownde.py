from redbot.core import app_commands, commands
import discord

class MrUnknownDE(commands.Cog):
    """Mein persönliches Info-Cog."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="mrunknown")
    async def mrunknown(self, interaction: discord.Interaction):
        """Zeigt Informationen über MrUnknownDE."""
        embed = discord.Embed(
            title="MrUnknownDE",
            description="Hey! I'm Unknown, a somewhat chaotic digital creature based in Germany. This site is the central hub for my VRChat experiments, IoT drink scales, and other side projects. Feel free to look around and poke at things!",
            color=discord.Color.purple(), # Ein schönes Lila als Akzentfarbe
            url="https://mrunk.de"
        )
        embed.set_thumbnail(url="https://mrunk.de/pic/profil_pic.webp") # Optionales Thumbnail, falls vorhanden
        embed.add_field(name="🌐 Webseite", value="[https://mrunk.de](https://mrunk.de)", inline=False)
        
        await interaction.response.send_message(embed=embed)
