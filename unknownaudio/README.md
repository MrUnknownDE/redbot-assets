# Unknown-Audio Cog

Ein Custom-Wrapper für das Kern-Audiosystem von Red-DiscordBot.

Dieses Cog stellt das mächtige (aber manchmal kompliziert zu bedienende) Redbot-Audiosystem in einer schönen, einsteigerfreundlichen Benutzeroberfläche bereit.

## 🔥 Features
- **Eigene Slash-Commands:** `/uplay`, `/upause`, `/uskip`, `/uview`
- **Konfliktfrei:** Nutzt den Prefix `u` (für Unknown), sodass administrative Standard-Befehle von Redbot (`[p]play`) immer noch problemlos funktionieren.
- **Interaktiver Player (`/uview`):** Zeigt den aktuell spielenden Song als 60-sekündigen Auto-Update Player an. Beinhaltet klickbare DJ-Tasten für Play/Pause, Skip & Stop.
- **Vote-Skip System:** Verhindert Trolle. Ein Klick auf "Skip" fragt das System nach einem Vote.

## 📥 Installation

```
[p]repo add mrunknownde-assets https://github.com/MrUnknownDE/redbot-assets
[p]cog install mrunknownde-assets unknownaudio
[p]load unknownaudio
[p]slash sync
```

*(Hinweis: Für die Wiedergabefunktionen muss das originale Redbot-Audio Cog konfiguriert und der Lavalink-Server gestartet sein!)*
