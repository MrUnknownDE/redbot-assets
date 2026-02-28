import discord
from redbot.core import commands
import aiohttp
from datetime import datetime

class Bierbaron(commands.Cog):
    """Bierbaron Commands and Stats."""

    def __init__(self, bot):
        self.bot = bot
        self.api_url = "https://live.der-bierbaron.de/api/vrchat.json"

    @commands.hybrid_command(name="bierbaron")
    async def info(self, ctx: commands.Context):
        """Informationen über den Bierbaron."""
        embed = discord.Embed(
            title="der-Bierbaron",
            description="Willkommen beim offiziellen Bierbaron Discord-System.\nHier dreht sich alles um das Trinken in VRChat.",
            color=discord.Color.gold(),
            url="https://der-bierbaron.de"
        )
        embed.add_field(name="🌐 Webseite", value="[der-bierbaron.de](https://der-bierbaron.de)", inline=True)
        embed.add_field(name="📡 Live Stats", value="[live.der-bierbaron.de](https://live.der-bierbaron.de)", inline=True)
        embed.set_footer(text="Bierbaron VRChat Projekt")
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="bierbaron-live")
    async def live(self, ctx: commands.Context):
        """Live-Informationen vom Server."""
        await ctx.typing()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.api_url) as response:
                    if response.status != 200:
                        return await ctx.send(f"Fehler! API gab Status-Code {response.status} zurück.")
                    data = await response.json()
        except Exception as e:
            return await ctx.send(f"Fehler beim Abrufen der API: {e}")

        # Parse Data
        server_info = data.get("server", {})
        aggregate = data.get("aggregate", {})
        users = data.get("users", [])
        last_prost = data.get("lastProst", {})

        online_players = server_info.get("onlinePlayers", 0)
        avg_vol = aggregate.get("averageVolume_ml", 0)
        avg_fill = aggregate.get("averageFillLevel", 0)

        embed = discord.Embed(
            title="🍺 der-Bierbaron Live Server",
            color=discord.Color.from_rgb(255, 165, 0), # Orange/Gold für Bier
            timestamp=discord.utils.utcnow()
        )
        
        embed.add_field(name="👥 Online", value=f"{online_players} Spieler", inline=True)
        embed.add_field(name="🧪 Ø Volumen", value=f"{avg_vol:.1f} ml", inline=True)
        embed.add_field(name="📊 Ø Füllstand", value=f"{avg_fill:.1f}%", inline=True)

        if users:
            user_list = ""
            # Wir sortieren nach der getrunkenen Menge heute absteigend und zeigen die Top 10 Online
            for idx, u in enumerate(sorted(users, key=lambda x: x.get('drinkedToday_ml', 0), reverse=True)[:10]):
                name = u.get("username", "Unknown")
                beverage = u.get("beverage", "N/A")
                drank = u.get("drinkedToday_ml", 0)
                filled = u.get("fillLevel", 0)
                user_list += f"**{idx+1}. {name}**: {beverage} ({drank}ml getrunken, Füllstand: {filled:.1f}%)\n"
            
            if user_list:
                embed.add_field(name="Aktive Trinker Online", value=user_list, inline=False)
        else:
             embed.add_field(name="Aktive Trinker", value="Derzeit niemand am Trinken.", inline=False)
        
        if last_prost:
            sender = last_prost.get("sender", "Jemand")
            recipient = last_prost.get("recipient", "Jemandem")
            message = last_prost.get("message", "Prost!")
            embed.add_field(name="Letztes Prost 🍻", value=f"**{sender}** an **{recipient}**:\n*\"{message}\"*", inline=False)

        await ctx.send(embed=embed)
