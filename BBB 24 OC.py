import discord
from discord.ext import commands
from discord_slash import SlashCommand  # type: ignore

bot = commands.Bot(command_prefix="!")
slash = SlashCommand(bot, sync_commands=True)

import asyncio
import random
import json
from datetime import datetime

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

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



# Store warnings and AFK status in a JSON file (or database)
warnings = {}
afk_status = {}


LOG_CHANNEL_ID = 1362177980364755034  

# Warning command
@bot.command(name='warn')
async def warn(ctx, member: discord.Member, *, reason=None):
    if reason is None:
        reason = ""
    
    # Log the warning in the JSON file
    if member.id not in warnings:
        warnings[member.id] = []
    warnings[member.id].append({"reason": reason, "date": str(datetime.utcnow())})
    
    with open('warnings.json', 'w') as f:
        json.dump(warnings, f, indent=4)
    
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    await log_channel.send(f"**{member}** was warned for: {reason}")
    await ctx.send(f"{member.mention} has been warned for: {reason}")
    
    # Optionally, send them a DM
    await member.send(f"You've been warned in {ctx.guild.name} for: {reason}")

# Mute command (disabling message sending)
@bot.command(name='mute')
async def mute(ctx, member: discord.Member, duration: int = 60, *, reason=None):
    if reason is None:
        reason = "No reason provided."
    
    # Mute permissions in each text channel
    for channel in ctx.guild.text_channels:
        await channel.set_permissions(member, send_messages=False, reason=reason)
    
    await ctx.send(f"{member.mention} has been muted for {duration} seconds for: {reason}")
    
    # Send a log in the specified log channel
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    await log_channel.send(f"{member} was muted for {duration} seconds for: {reason}")
    
    # Unmute after the specified duration
    await asyncio.sleep(duration)
    
    for channel in ctx.guild.text_channels:
        await channel.set_permissions(member, send_messages=True)
    
    await ctx.send(f"{member.mention} has been unmuted.")
    await log_channel.send(f"{member} has been unmuted.")

# Unmute command
@bot.command(name='unmute')
async def unmute(ctx, member: discord.Member):
    # Restore send message permissions
    for channel in ctx.guild.text_channels:
        await channel.set_permissions(member, send_messages=True)
    
    await ctx.send(f"{member.mention} has been unmuted.")
    
    # Log the unmute in the log channel
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    await log_channel.send(f"{member} has been unmuted.")

# Ban command
@bot.command(name='ban')
async def ban(ctx, member: discord.Member, *, reason=None):
    if reason is None:
        reason = "No reason provided."
    await member.ban(reason=reason)
    await ctx.send(f"{member.mention} has been banned for: {reason}")
    
    # Log the ban
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    await log_channel.send(f"{member} was banned for: {reason}")

# Purge command
@bot.command(name='purge')
async def purge(ctx, limit: int):
    await ctx.channel.purge(limit=limit)
    await ctx.send(f"Purged {limit} messages.")

# Poll command
@bot.command(name='poll')
async def poll(ctx, question: str, *options: str):
    if len(options) < 2:
        await ctx.send("You must provide at least two options.")
        return

    embed = discord.Embed(title="Poll", description=question, color=discord.Color.blue())
    for idx, option in enumerate(options, start=1):
        embed.add_field(name=f"Option {idx}", value=option, inline=False)
    message = await ctx.send(embed=embed)

    # React with numbered emojis
    for i in range(len(options)):
        await message.add_reaction(str(i + 1) + "\u20e3")

# Giveaway command
@bot.command(name='giveaway')
async def giveaway(ctx, duration: int, *, prize: str):
    await ctx.send(f"A giveaway for {prize} is starting! React to this message to enter!")
    
    # Add a reaction emoji for users to enter
    message = await ctx.send("React with 🎉 to enter!")
    await message.add_reaction("🎉")

    # Wait for the giveaway to end
    await asyncio.sleep(duration)
    
    # Fetch reactions
    message = await ctx.fetch_message(message.id)
    users = await message.reactions[0].users().flatten()
    users = [user for user in users if user != bot.user]

    if users:
        winner = random.choice(users)
        await ctx.send(f"🎉 {winner.mention} won the giveaway for {prize}!")
    else:
        await ctx.send("No one entered the giveaway.")
    
    # Giveaway Reroll command
    @bot.command(name="reroll")
    async def reroll(ctx):
        if len(users) > 0:
            winner = random.choice(users)
            await ctx.send(f"🎉 The new winner for the giveaway is: {winner.mention}")
        else:
            await ctx.send("No participants for the giveaway.")

# AFK command
@bot.command(name='afk')
async def afk(ctx, *, reason="AFK"):
    afk_status[ctx.author.id] = reason
    await ctx.send(f"{ctx.author.mention} is now AFK. Reason: {reason}")

@bot.event
async def on_message(message):
    if message.author.id in afk_status:
        # Check if the message mentions an AFK user
        if message.mentions:
            for user in message.mentions:
                if user.id == message.author.id:
                    await message.channel.send(f"{message.author.mention} is AFK: {afk_status[message.author.id]}")
    
    # Remove AFK status when a user sends a message
    if message.author.id in afk_status:
        del afk_status[message.author.id]
    
    await bot.process_commands(message)



# Start the bot
bot.run('tokMTM4Njc1ODY5ODY0NjUwNzc1MQ.GCHfGX.Tb2XQ3_fIP8AnNFXF5Gs9UQML5IKouqy8Y_r2A')

