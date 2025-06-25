from discord.ext import commands
from discord_slash import SlashCommand  # type: ignore # type: i
bot = commands.Bot(command_prefix="/")
slash = SlashCommand(bot, sync_commands=True)

@bot.event
async def on_ready():
    print("Bot is ready!")
    guild = bot.get_guild(1357656640526094398)
    await slash.add_slash_command(clear_messages, guild_ids=[guild.id])

@slash.slash(name='purge', description='Clear a certain number of messages from the channel')
async def clear_messages(ctx, amount: int = 100):
    await ctx.message.delete()
    await ctx.channel.purge(limit=amount)

@bot.event
async def on_message(message):
    if message.content.startswith("/"):
        await message.channel.send("Available commands: /purge")
        