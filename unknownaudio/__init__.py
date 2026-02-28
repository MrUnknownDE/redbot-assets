from .unknownaudio import UnknownAudio

async def setup(bot):
    await bot.add_cog(UnknownAudio(bot))
