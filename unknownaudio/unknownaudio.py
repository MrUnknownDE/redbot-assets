import discord
import asyncio
from typing import Optional
from redbot.core import app_commands, commands
from redbot.core.utils.chat_formatting import humanize_timedelta

class AudioControlView(discord.ui.View):
    """Interaktive Buttons für das Audio System."""
    def __init__(self, cog: commands.Cog, guild_id: int):
        super().__init__(timeout=60) # Die Buttons funktionieren für 60 Sekunden
        self.cog = cog
        self.guild_id = guild_id
        
    async def get_audio_cog(self):
        return self.cog.bot.get_cog("Audio")

    @discord.ui.button(label="Play / Pause", style=discord.ButtonStyle.primary, emoji="⏯️")
    async def toggle_playback(self, interaction: discord.Interaction, button: discord.ui.Button):
        audio_cog = await self.get_audio_cog()
        if not audio_cog:
            return await interaction.response.send_message("Das Audio-System ist nicht geladen.", ephemeral=True)
            
        try:
            # Redbot Audio Cog verwendet Kontext-Befehle. Wir simulieren das Verhalten grob 
            # oder greifen auf die internen API-Funktionen von Lavalink zu.
            # Da direkter Zugriff auf redbot.cogs.audio komplex ist, leiten wir auf die commands um.
            
            # Hinweis: Für ein sauberes Wrapper-Cog rufen wir die Methoden des Audio cogs ab.
            # Um es simpel zu halten, senden wir eine Nachricht, die den Befehl auslöst.
            # Disclaimer: In einer echten Umgebung greifen wir hier auf lavalink player zu.
            player = getattr(audio_cog, "get_player", lambda x: None)(interaction.guild)
            if not player:
                 return await interaction.response.send_message("Es spielt gerade nichts.", ephemeral=True)
            
            if player.paused:
                await player.resume()
                await interaction.response.send_message("▶️ Wiedergabe fortgesetzt.", ephemeral=True)
            else:
                await player.pause()
                await interaction.response.send_message("⏸️ Wiedergabe pausiert.", ephemeral=True)
        except Exception as e:
             await interaction.response.send_message(f"Fehler: {e}", ephemeral=True)

    @discord.ui.button(label="Skip", style=discord.ButtonStyle.secondary, emoji="⏭️")
    async def skip_track(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Leitet zur Skip-Logik weiter
        await self.cog.process_skip(interaction)

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger, emoji="⏹️")
    async def stop_playback(self, interaction: discord.Interaction, button: discord.ui.Button):
        audio_cog = await self.get_audio_cog()
        if not audio_cog:
            return await interaction.response.send_message("Das Audio-System ist nicht geladen.", ephemeral=True)
        
        try:
            player = getattr(audio_cog, "get_player", lambda x: None)(interaction.guild)
            if player:
                await player.stop()
                await interaction.response.send_message("⏹️ Wiedergabe gestoppt und Queue geleert.", ephemeral=False)
            else:
                 await interaction.response.send_message("Nichts zu stoppen.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Fehler: {e}", ephemeral=True)

class UnknownAudio(commands.Cog):
    """Unknown-Audio Wrapper für Redbot."""

    def __init__(self, bot):
        self.bot = bot
        self.skip_votes = {} # Dictionary um Abstimmungen zu tracken {guild_id: set(user_ids)}

    async def get_audio_cog(self):
        """Hilfsfunktion um prüfen zu können, ob das Original-Audio Cog da ist."""
        return self.bot.get_cog("Audio")

    async def get_player(self, guild):
         audio_cog = await self.get_audio_cog()
         if audio_cog:
             # Redbot's lavalink integriert (redbot.cogs.audio.core.utilities)
             # Wir greifen auf die standard get_player methode zu wenn verfügbar
             try:
                 import lavalink
                 return lavalink.get_player(guild.id)
             except (ImportError, AttributeError):
                 return None
         return None

    def create_player_embed(self, player) -> discord.Embed:
        """Erstellt ein schönes Embed für den aktuellen Status."""
        if not player or not player.current:
            return discord.Embed(
                title="🎧 Unknown-Audio Player",
                description="Derzeit wird nichts abgespielt.",
                color=discord.Color.dark_gray()
            )
            
        track = player.current
        
        position_sec = int(player.position / 1000) if player.position else 0
        length_sec = int(track.length / 1000) if track.length else 0
        
        # Format time MM:SS
        pos_str = f"{position_sec // 60:02d}:{position_sec % 60:02d}"
        len_str = f"{length_sec // 60:02d}:{length_sec % 60:02d}" if not track.is_stream else "LIVE"
        
        # Mini Fortschrittsbalken
        progress = 0
        if length_sec > 0:
            progress = int((position_sec / length_sec) * 10)
        
        bar_str = "▬" * progress + "🔘" + "▬" * (10 - progress)
        
        status = "⏸️ Pausiert" if player.paused else "▶️ Spielt"
        
        embed = discord.Embed(
            title=f"{status}: {track.title}",
            url=track.uri,
            color=discord.Color.purple()
        )
        embed.set_author(name="Unknown-Audio", icon_url=self.bot.user.display_avatar.url)
        embed.description = f"Von: **{track.author}**\n\n`{pos_str}` {bar_str} `{len_str}`"
        
        if track.thumbnail:
            embed.set_thumbnail(url=track.thumbnail)
            
        embed.set_footer(text="Requested via Unknown-Audio Wrapper")
        return embed

    @app_commands.command(name="uview")
    async def uview(self, interaction: discord.Interaction):
        """Öffnet das interaktive Audio-Live-Panel für 60 Sekunden."""
        player = await self.get_player(interaction.guild)
        if not player or not player.current:
            return await interaction.response.send_message("Es wird aktuell nichts abgespielt.", ephemeral=True)

        view = AudioControlView(self, interaction.guild.id)
        embed = self.create_player_embed(player)
        
        await interaction.response.send_message(embed=embed, view=view)
        original_msg = await interaction.original_response()

        # Background Update Task for 1 Minute (12 updates every 5 seconds)
        async def update_panel():
            for _ in range(12):
                await asyncio.sleep(5)
                # Check ob Player noch existiert
                current_player = await self.get_player(interaction.guild)
                if not current_player or not current_player.current:
                    break
                
                try:
                    await original_msg.edit(embed=self.create_player_embed(current_player))
                except discord.NotFound:
                    break # Nachricht wurde gelöscht
                except Exception:
                    pass
            
            # Timeout: Entferne Buttons
            try:
                final_embed = self.create_player_embed(await self.get_player(interaction.guild))
                final_embed.set_footer(text="Live-View beendet. Nutze /uview für ein neues Fenster.")
                await original_msg.edit(embed=final_embed, view=None)
            except Exception:
                pass
                
        # Starte den Updater im Hintergrund
        self.bot.loop.create_task(update_panel())

    @app_commands.command(name="uplay")
    @app_commands.describe(query="Der Name des Songs oder ein Link (Youtube, Spotify etc.)")
    async def uplay(self, interaction: discord.Interaction, query: str):
        """Spielt einen Song ab und öffnet das Live-Panel."""
        audio_cog = await self.get_audio_cog()
        if not audio_cog:
            return await interaction.response.send_message("Das Kern-Audiosystem ist nicht aktiv.", ephemeral=True)
            
        # Wir müssen den User zwingen im Voice Channel zu sein
        if not interaction.user.voice or not interaction.user.voice.channel:
            return await interaction.response.send_message("Du bist in keinem Voice-Channel!", ephemeral=True)
            
        await interaction.response.defer()
        
        # Redbot's Audio Core erfordert Context. Wir erzeugen einen künstlichen Context 
        # um die standard Befehle auszulösen, das ist der sicherste Weg mit Redbot.
        ctx = await commands.Context.from_interaction(interaction)
        
        # Nutze die Redbot Audio enqueue routing
        try:
             # Dies simuliert den Aufruf von [p]play
             msg = ctx.message
             msg.content = f"{ctx.prefix}play {query}"
             await self.bot.process_commands(msg)
             
             # Kurze Verzögerung für Lavalink zum Laden
             await asyncio.sleep(2)
             
             # Sende unsere View hinterher
             player = await self.get_player(interaction.guild)
             if player and player.current:
                 view = AudioControlView(self, interaction.guild.id)
                 embed = self.create_player_embed(player)
                 await interaction.followup.send("🎶 Audiosystem gestartet:", embed=embed, view=view)
             else:
                  await interaction.followup.send("Song wurde wahrscheinlich der Warteschlange hinzugefügt.")
        except Exception as e:
             await interaction.followup.send(f"Fehler beim Verbinden mit dem Audiosystem: {e}")

    @app_commands.command(name="upause")
    async def upause(self, interaction: discord.Interaction):
        """Pausiert oder setzt die Wiedergabe fort (Toggle)."""
        player = await self.get_player(interaction.guild)
        if not player:
            return await interaction.response.send_message("Es spielt gerade nichts.", ephemeral=True)
            
        if player.paused:
            await player.resume()
            await interaction.response.send_message("▶️ Wiedergabe fortgesetzt.")
        else:
            await player.pause()
            await interaction.response.send_message("⏸️ Wiedergabe pausiert.")

    async def process_skip(self, interaction: discord.Interaction):
        """Die Logik für das Skip-Voting, aufgerufen durch Command oder Button."""
        player = await self.get_player(interaction.guild)
        if not player or not player.current:
            if not interaction.response.is_done():
                await interaction.response.send_message("Es gibt nichts zum Skippen.", ephemeral=True)
            return

        voice_channel = interaction.guild.me.voice.channel if interaction.guild.me and interaction.guild.me.voice else None
        if not voice_channel or interaction.user not in voice_channel.members:
             return await interaction.response.send_message("Du musst im selben Voice-Channel sein, um zu skippen!", ephemeral=True)

        user_count = sum(1 for m in voice_channel.members if not m.bot)
        required_votes = int(user_count / 2) + 1 if user_count > 2 else 1

        guild_id = interaction.guild.id
        if guild_id not in self.skip_votes:
            self.skip_votes[guild_id] = set()
            
        self.skip_votes[guild_id].add(interaction.user.id)
        current_votes = len(self.skip_votes[guild_id])

        # Wenn der Typ ein Admin ist oder alleine im Channel, oder genug Votes
        if interaction.user.guild_permissions.administrator or current_votes >= required_votes:
             await player.skip()
             self.skip_votes[guild_id].clear()
             msg = "⏭️ Song erfolgreich übersprungen!"
             if interaction.response.is_done():
                  await interaction.followup.send(msg)
             else:
                  await interaction.response.send_message(msg)
        else:
             msg = f"🗳️ Skip-Vote registriert: **{current_votes}/{required_votes}** benötigte Stimmen.\nNutze `/uskip` oder den Skip-Button."
             if interaction.response.is_done():
                  await interaction.followup.send(msg)
             else:
                  await interaction.response.send_message(msg)

    @app_commands.command(name="uskip")
    async def uskip(self, interaction: discord.Interaction):
        """Startet einen Vote zum Überspringen des aktuellen Songs."""
        await self.process_skip(interaction)
