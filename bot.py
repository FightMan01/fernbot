import aiohttp
import discord
import asyncio
from discord.ext import commands
from discord.ext.commands import Bot
import datetime, time
import os
import youtube_dl
from discord.voice_client import VoiceClient
global playing
playing = "No music playing right now :("
players = {}
global chat_filter
global bypass_list
client = commands.Bot(command_prefix='/')
Client = discord.Client()

@client.event
async def on_ready():
    print ("The bot is ready to use.")
    print ("Name: " + client.user.name)
    print ("ID: " + client.user.id)

@client.command(pass_context=True)
async def ping(ctx):
    '''A ping command'''
    if not ctx.message.author.bot:
        channel = ctx.message.channel
        t1 = time.perf_counter()
        await client.send_typing(channel)
        t2 = time.perf_counter()
        embed=discord.Embed(title="Pong!", description='This message took around {}ms.'.format(round((t2-t1)*1000)), color=0xffff00)
        await client.say(embed=embed)
    else:
        return False

@client.command(pass_context=True)
async def purge(ctx, amount=301):
    '''Usage: /purge [amount]'''
    if ctx.message.author.server_permissions.administrator or ctx.message.author.id == '416226732966936577':
        try:
            channel = ctx.message.channel
            messages = []
            async for message in client.logs_from(channel, limit=int(amount) + 1):
                messages.append(message)
            await client.delete_messages(messages)
            await client.say(":white_check_mark: Messages deleted. :thumbsup:")
        except:
            print (Exception)
            await client.say("The number must be between 1 and 300 and the message be maximum 14 days old.:x:")
    else:
        await client.say("You need Admin perms to use this. :x:")

@client.command(pass_context=True, no_pm=True)
async def kick(ctx, user: discord.Member, * ,reason : str = None):
    '''Usage: /kick [member] [reason]'''
    if not ctx.message.author.bot:
        if ctx.message.author.server_permissions.administrator:
            if reason == "None":
                reason = "(No reason logged!)"
            await client.send_message(user, "You're kicked from **{}** server for this reason: **".format(ctx.message.server.name) + reason + "**")
            await client.say("Bye, {}. You got kicked :D".format(user.mention))
            await client.kick(user)  
        else:
            await client.say("You need Admin prems to use this! :x:")
    else:
        return False

@client.command(pass_context=True)
async def serverinfo(ctx):
    '''A useful command.'''
    if not ctx.message.author.bot:
        online = 0
        for i in ctx.message.server.members:
            if str(i.status) == 'online' or str(i.status) == 'idle' or str(i.status) == 'dnd':
                online += 1
        role_count = len(ctx.message.server.roles)
        emoji_count = len(ctx.message.server.emojis)
        embed = discord.Embed(title="Information from this server: {}".format(ctx.message.server.name), description="Here it is:", color=0x00ff00)
        embed.add_field(name="Name: ", value=ctx.message.server.name, inline=True)
        embed.add_field(name="ID: ", value=ctx.message.server.id, inline=True)
        embed.add_field(name="Number of roles: ", value=len(ctx.message.server.roles), inline=True)
        embed.add_field(name="Members: ", value=len(ctx.message.server.members))
        embed.add_field(name='Currently online', value=online)
        embed.add_field(name="Server created at: ", value=ctx.message.server.created_at.__format__('%A, %Y. %m. %d. @ %H:%M:%S'), inline=True)
        embed.add_field(name="Channel crated at: ",value=ctx.message.channel.created_at.__format__('%A, %Y. %m. %d. @ %H:%M:%S'), inline=True)
        embed.add_field(name="Current channel: ",value=ctx.message.channel, inline=True)
        embed.add_field(name="Server owner's name: ",value=ctx.message.server.owner.mention, inline=True)
        embed.add_field(name="Server owner's status: ",value=ctx.message.server.owner.status, inline=True)
        embed.add_field(name="Server region: ",value=ctx.message.server.region, inline=True)
        embed.add_field(name='Moderation level', value=str(ctx.message.server.verification_level))
        embed.add_field(name='Number of emotes', value=str(emoji_count))
        embed.add_field(name='Highest role', value=ctx.message.server.role_hierarchy[0])
        embed.set_thumbnail(url=ctx.message.server.icon_url)
        embed.set_author(name=ctx.message.server.name, icon_url=ctx.message.server.icon_url)
        await client.say(embed=embed)
    else:
        return False

@client.command(pass_context=True)
async def leave(ctx):
    '''Bot leave the voice channel.'''
    if not ctx.message.author.bot:
        try:
            server = ctx.message.server
            voice_client = client.voice_client_in(server)
            await voice_client.disconnect()
            await client.say("I'm left the voice channel. :thumbsup:")
        except:
            await client.say("I'm not in a voice channel. :x:")
    else:
        return False

@client.command(aliases=['p'], pass_context=True)
async def play(ctx, * ,url, ytdl_options=None, **kwarg):
    '''Usage: /play [music]'''
    if not ctx.message.author.bot:
        server = ctx.message.server
        voice_client = client.voice_client_in(server)
        if voice_client == None:
            await client.say("Please wait. :musical_note:")
            try:
                channel = ctx.message.author.voice.voice_channel
                await client.join_voice_channel(channel)
            except:
                return False
            try:
                server = ctx.message.server
                voice_client = client.voice_client_in(server)
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp4',
                        'preferredquality': '192',
                    }],
                }
                player = await voice_client.create_ytdl_player("ytsearch: {}".format(url), before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5")
                player.start()
                global players
                players[server.id] = player 
                player.volume = 0.2
                global playing 
                playing = "Now playing: **{}**".format(player.title)
                global last_played
                last_played = player.url
                await client.say("The music started! :thumbsup:")
            except:
                print(Exception)
                await client.say("Oops! Something went wrong. Please try /leave and try again. :x:")
            while not player.is_done():
                await asyncio.sleep(1) 
            try:
                server = ctx.message.server
                voice_client = client.voice_client_in(server)
                await voice_client.disconnect()
                await client.say("The song is over. I left the voice channel. :white_check_mark: ")
            except:
                return False
        else:
             await client.say("It seems like I currently playing something! Please try /leave and try again. :x:")
    else:
        return False

@client.command(pass_context=True)
async def pause(ctx):
    if not ctx.message.author.bot:
        try:
            id = ctx.message.server.id
            players[id].pause()
            await client.say("Paused. :thumbsup:")
        except:
            await client.say("The song is already paused. :x:")
    else:
        return False

@client.command(pass_context=True)
async def resume(ctx):
    if not ctx.message.author.bot:
        try:
            id = ctx.message.server.id
            players[id].resume()
            await client.say("Resumed. :thumbsup:")
        except:
            await client.say("The song is already playing or stopped. :x:")
    else:
        return False

@client.command(pass_context=True)
async def stop(ctx):
    if not ctx.message.author.bot:
        try:
            id = ctx.message.server.id
            players[id].stop()
            server = ctx.message.server
            voice_client = client.voice_client_in(server)
            await voice_client.disconnect()
            await client.say("Stopped. :white_check_mark:")
        except:
            await client.say("The song is already stopped. :x:")
    else:
        return False

@client.command(aliases=['np'], pass_context=True)
async def now(ctx):
    if not ctx.message.author.bot:
        global playing
        await client.say(playing)
    else:
        return False

@client.command(pass_context = True)
async def ban(ctx, member: discord.Member, days: int, *, reason : str = None):
    if ctx.message.author.server_permissions.administrator:
        await client.send_message(member, "You got banned from this server {} for {} days for this reason: **{}**".format(ctx.message.server.name, days ,reason)) 
        await client.say(":white_check_mark: I banned this member! :thumbsup:")
        await client.ban(member, days)
    else:
        await client.say("You need Admin perms to use this :x:")

client.run(os.environ.get('TOKEN'))
