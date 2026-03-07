import discord
import aiohttp
import asyncio
import logging
from discord import app_commands
from redbot.core import commands, Config

log = logging.getLogger("red.bierbaron")

API_URL = "https://live.der-bierbaron.de/api/vrchat.json"

class Bierbaron(commands.Cog):
    """Bierbaron Commands and Stats."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=9483726154, force_registration=True)
        self.config.register_guild(live_channel=None, live_message=None)
        self._live_task: asyncio.Task | None = None

    async def cog_load(self):
        """Called by Redbot after the cog is fully loaded."""
        self._live_task = asyncio.create_task(self._live_loop())

    def cog_unload(self):
        if self._live_task:
            self._live_task.cancel()

    async def _live_loop(self):
        """Background loop that updates all live embeds every 15 seconds."""
        await self.bot.wait_until_red_ready()
        while True:
            await self._run_live_update()
            await asyncio.sleep(15)

    async def _fetch_api_data(self):
        """Fetches data from the Bierbaron API. Returns None on failure."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(API_URL, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status != 200:
                        log.warning(f"Bierbaron API returned {response.status}")
                        return None
                    return await response.json()
        except Exception as e:
            log.error(f"Error fetching Bierbaron API: {e}")
            return None

    def _build_live_embed(self, data: dict) -> discord.Embed:
        """Builds the live stats embed from API data."""
        server_info = data.get("server", {})
        aggregate = data.get("aggregate", {})
        users = data.get("users", [])
        last_prost = data.get("lastProst", {})

        online_players = server_info.get("onlinePlayers", 0)
        avg_vol = aggregate.get("averageVolume_ml", 0)
        avg_fill = aggregate.get("averageFillLevel", 0)

        embed = discord.Embed(
            title="🍺 der-Bierbaron – Live Server",
            description=(
                "Willkommen auf dem **Live-Server des Bierbar­ons**!\n"
                "Hier übertragen alle aktiven Teilnehmer ihren Füllstand\n"
                "fast in Echtzeit aus VRChat. Trinkt ihr mit?\n\n"
                "[🌐 Webseite](https://der-bierbaron.de)  ·  "
                "[📡 Live-Dashboard](https://live.der-bierbaron.de)"
            ),
            color=discord.Color.from_rgb(255, 140, 0),
            timestamp=discord.utils.utcnow()
        )
        embed.set_footer(text="Aktualisiert alle 15 Sek. · der-Bierbaron Live")

        # Server Stats
        embed.add_field(name="👥 Spieler Online", value=f"**{online_players}**", inline=True)
        embed.add_field(name="🧪 Ø Volumen", value=f"**{avg_vol:.1f} ml**", inline=True)
        embed.add_field(name="📊 Ø Füllstand", value=f"**{avg_fill:.1f} %**", inline=True)

        # User table
        if users:
            lines = []
            for idx, u in enumerate(
                sorted(users, key=lambda x: x.get("drinkedToday_ml", 0), reverse=True)[:10]
            ):
                name = u.get("username", "Unknown")
                bev = u.get("beverage", "?")
                drank = u.get("drinkedToday_ml", 0)
                fill = u.get("fillLevel", 0)

                # Simple fill bar (10 cells)
                fill_pct = max(0, min(fill, 100))
                filled_cells = round(fill_pct / 10)
                bar = "🟧" * filled_cells + "⬛" * (10 - filled_cells)

                lines.append(f"**{idx + 1}. {name}** – {bev}\n{bar} `{fill:.1f}%` · {drank} ml heute")

            embed.add_field(
                name=f"🏆 Trinker Online ({len(users)})",
                value="\n".join(lines) or "–",
                inline=False
            )
        else:
            embed.add_field(name="🏆 Trinker Online", value="Derzeit niemand aktiv.", inline=False)

        # Last Prost
        if last_prost:
            sender = last_prost.get("sender", "?")
            recipient = last_prost.get("recipient", "?")
            msg = last_prost.get("message", "Prost!")
            embed.add_field(
                name="🍻 Letztes Prost",
                value=f"**{sender}** trank auf **{recipient}**:\n*„{msg}"*",
                inline=False
            )

        return embed

    # ── Background task ──────────────────────────────────────────────────────

    async def _run_live_update(self):
        """Fetches API data and updates all registered live embeds."""
        data = await self._fetch_api_data()
        if not data:
            return

        embed = self._build_live_embed(data)
        all_guilds = await self.config.all_guilds()

        for guild_id, cfg in all_guilds.items():
            channel_id = cfg.get("live_channel")
            message_id = cfg.get("live_message")
            if not channel_id or not message_id:
                continue

            guild = self.bot.get_guild(guild_id)
            if not guild:
                continue
            channel = guild.get_channel(channel_id)
            if not channel:
                continue

            try:
                message = await channel.fetch_message(message_id)
                await message.edit(embed=embed)
            except discord.NotFound:
                await self.config.guild(guild).live_message.set(None)
                await self.config.guild(guild).live_channel.set(None)
                log.info(f"Live embed message not found in guild {guild_id}, cleared config.")
            except discord.Forbidden:
                log.warning(f"Missing permission to edit live embed in guild {guild_id}.")
            except asyncio.CancelledError:
                raise
            except Exception as e:
                log.error(f"Error updating live embed in guild {guild_id}: {e}")

    # ── Slash Commands ────────────────────────────────────────────────────────

    @app_commands.command(name="bierbaron")
    async def info(self, interaction: discord.Interaction):
        """Informationen über den Bierbaron."""
        embed = discord.Embed(
            title="der-Bierbaron",
            description=(
                "Willkommen beim offiziellen **Bierbaron** Discord-System.\n"
                "Hier dreht sich alles ums Trinken in VRChat – Gläser, Scales und Echtzeit-Stats."
            ),
            color=discord.Color.gold(),
            url="https://der-bierbaron.de"
        )
        embed.add_field(name="🌐 Webseite", value="[der-bierbaron.de](https://der-bierbaron.de)", inline=True)
        embed.add_field(name="📡 Live Stats", value="[live.der-bierbaron.de](https://live.der-bierbaron.de)", inline=True)
        embed.set_footer(text="Bierbaron VRChat Projekt")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="bierbaron-live")
    async def live(self, interaction: discord.Interaction):
        """Zeige einen einmaligen Live-Snapshot des Bierbaron-Servers."""
        await interaction.response.defer()
        data = await self._fetch_api_data()
        if data is None:
            return await interaction.followup.send(
                "❌ Fehler beim Abrufen der Bierbaron-API. Bitte später erneut versuchen."
            )
        await interaction.followup.send(embed=self._build_live_embed(data))

    # ── Bot-Owner-only management commands ───────────────────────────────────

    @app_commands.command(name="bierbaron-setlive")
    @app_commands.describe(channel="Kanal für das automatisch aktualisierende Live-Embed.")
    async def setlive(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """[Bot-Owner] Startet das permanente Live-Embed in einem Kanal (alle 15 Sek.)."""
        if not await self.bot.is_owner(interaction.user):
            return await interaction.response.send_message(
                "⛔ Nur der Bot-Owner kann diesen Befehl verwenden.", ephemeral=True
            )

        await interaction.response.defer(ephemeral=True)

        # Remove old embed if present
        old_ch_id = await self.config.guild(interaction.guild).live_channel()
        old_msg_id = await self.config.guild(interaction.guild).live_message()
        if old_ch_id and old_msg_id:
            old_ch = interaction.guild.get_channel(old_ch_id)
            if old_ch:
                try:
                    old_msg = await old_ch.fetch_message(old_msg_id)
                    await old_msg.delete()
                except discord.NotFound:
                    pass

        data = await self._fetch_api_data()
        if data is None:
            return await interaction.followup.send("❌ Konnte die API nicht erreichen.")

        try:
            msg = await channel.send(embed=self._build_live_embed(data))
            await self.config.guild(interaction.guild).live_channel.set(channel.id)
            await self.config.guild(interaction.guild).live_message.set(msg.id)
            await interaction.followup.send(
                f"✅ Live-Embed in {channel.mention} gestartet. Es wird alle **15 Sekunden** aktualisiert."
            )
        except discord.Forbidden:
            await interaction.followup.send("❌ Ich habe keine Berechtigung, in diesem Kanal zu schreiben.")
        except Exception as e:
            await interaction.followup.send(f"❌ Fehler: {e}")

    @app_commands.command(name="bierbaron-stoplive")
    async def stoplive(self, interaction: discord.Interaction):
        """[Bot-Owner] Stoppt das permanente Live-Embed auf diesem Server."""
        if not await self.bot.is_owner(interaction.user):
            return await interaction.response.send_message(
                "⛔ Nur der Bot-Owner kann diesen Befehl verwenden.", ephemeral=True
            )

        await interaction.response.defer(ephemeral=True)

        channel_id = await self.config.guild(interaction.guild).live_channel()
        message_id = await self.config.guild(interaction.guild).live_message()

        if not channel_id:
            return await interaction.followup.send("ℹ️ Es läuft kein Live-Embed auf diesem Server.")

        # Try to delete the embed message
        channel = interaction.guild.get_channel(channel_id)
        if channel and message_id:
            try:
                msg = await channel.fetch_message(message_id)
                await msg.delete()
            except discord.NotFound:
                pass
            except discord.Forbidden:
                await interaction.followup.send(
                    "⚠️ Konnte die Live-Embed-Nachricht nicht löschen (fehlende Berechtigung), "
                    "aber das Auto-Update wurde deaktiviert."
                )

        await self.config.guild(interaction.guild).live_channel.set(None)
        await self.config.guild(interaction.guild).live_message.set(None)
        await interaction.followup.send("✅ Live-Embed wurde gestoppt und die Nachricht gelöscht.")
