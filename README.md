# MrUnknownDE Redbot Cogs

Willkommen in meinem Custom Repository für [Red-DiscordBot](https://github.com/Cog-Creators/Red-DiscordBot) Cogs! 🎉

Dieses Repository enthält verschiedene kleine Cogs und Erweiterungen, die ich für meine Projekte (wie VRChat und den Bierbaron) erstellt habe.

## 📥 Installation

Um diese Cogs auf deinem eigenen Redbot zu installieren, folge diesen einfachen Schritten:

1. **Füge das Repository zu deinem Bot hinzu:**
   Nutze diesen Befehl im Discord-Chat deines Bots (ersetze `[p]` durch deinen Prefix, z.B. `!`):
   ```
   [p]repo add mrunknownde-assets https://github.com/MrUnknownDE/redbot-assets
   ```

2. **Installiere den gewünschten Cog:**
   Um zum Beispiel das `bierbaron`-Cog zu installieren, tippe:
   ```
   [p]cog install mrunknownde-assets bierbaron
   ```

3. **Lade das Cog:**
   ```
   [p]load bierbaron
   ```

---

## 📦 Verfügbare Cogs

Hier ist eine Liste der aktuell verfügbaren Cogs in diesem Repository:

### 1. `mrunknownde`
Ein kleines Info-Cog, das Details über mich, meine Projekte und meine Webseite bereitstellt.
- **Befehle:**
  - `[p]mrunknown` (bzw. `/mrunknown`): Zeigt ein kleines Profil-Embed an.

### 2. `bierbaron`
Das offizielle Cog für das VRChat-Projekt "Der Bierbaron". Verbindet sich direkt mit der Bierbaron-API, um Live-Trinkstatistiken von VRChat abzurufen.
- **Befehle:**
  - `[p]info` (bzw. `/info`): Allgemeine Infos über das Projekt.
  - `[p]live` (bzw. `/live`): Holt die Live-Statistiken, Leaderboards für den Abend und das letzte "Prost!" direkt aus VRChat.
- **Voraussetzungen:** Benötigt das Python Package `aiohttp`.

### 3. `unknownaudio` (Unknown-Audio)
Ein interaktiver Benutzeroberflächen-Wrapper für das Kern-Audiosystem (Lavalink) von Redbot.
- **Interaktives UI:** Ersetzt das Tippen von Befehlen durch moderne, anklickbare Buttons (Play/Pause, Skip, Stop).
- **Auto-Updating Player:** `/uview` generiert ein Interface, das sich eine Minute lang live aktualisiert.
- **Vote-Skip System:** `/uskip` oder der DJ-Button ermöglichen demokratisches Skippen von Titeln.
- **Befehle:**
  - `/uplay <song>`
  - `/uview`
  - `/upause`
  - `/uskip`

---
*Erstellt & gepflegt von [MrUnknownDE](https://mrunk.de).*
