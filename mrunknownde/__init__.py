from .mrunknownde import MrUnknownDE

async def setup(bot):
    await bot.add_cog(MrUnknownDE(bot))
