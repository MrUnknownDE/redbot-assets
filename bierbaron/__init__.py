from .bierbaron import Bierbaron

async def setup(bot):
    await bot.add_cog(Bierbaron(bot))
