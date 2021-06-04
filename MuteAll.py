import discord
from discord.ext import commands
import random
import os
# import asyncio

TOKEN = open("token.txt", "r").read()

EXEMPT_ROLES = open("exempt_roles.txt", "r").read().split(",")

client = commands.AutoShardedBot(command_prefix=".")

client.remove_command("help")  # removes the default ".help" command

# sets status when the bot is ready
@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online)
    print("Ready!")


# send a help msg when the bot joins a server
@client.event
async def on_guild_join(guild):
    embed = discord.Embed()
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            embed.add_field(name="Hey, thanks for adding me!", value="If you are already in a voice channel, please reconnect everyone. Type `.help` to view all the commands.")
            await channel.send(embed=embed)
            break


# invite link for the bot
@client.command(aliases=["i", "link"])
async def invite(ctx):
    embed = discord.Embed()
    embed.add_field(name="Invite Link", value="[Invite The Bot](https://discord.com/api/oauth2/authorize?client_id=850398067504840784&permissions=281226240&scope=bot)")
    await ctx.send(embed=embed)


# shows latency of the bot
@client.command(aliases=["latency"])
async def ping(ctx):
    embed = discord.Embed()
    embed.add_field(name="Ping", value=f"{round(client.latency * 1000)} ms")
    await ctx.send(embed=embed)


# shows help text
@client.command(aliases=["commands", "Help", "h", "H"])
async def help(ctx):
    embed = discord.Embed(color=discord.Color.lighter_grey())

    embed.set_author(name="Available Commands")

    embed.add_field(name="`.ping`", value="Latency of the bot", inline=False)

    embed.add_field(name="`.invite`", value="Invite link", inline=False)

    embed.add_field(name="`.mute` / `.m`", value="Mute humans and un-mute bots in your current voice channel.",
                    inline=False)

    embed.add_field(name="`.unmute` / `.u`", value="Un-mute humans and mute bots in your current voice channel.",
                    inline=False)

    embed.add_field(name="`.deafen` / `.d`", value="Deafen everyone in your current voice channel.",
                    inline=False)

    embed.add_field(name="`.undeafen` / `.ud`", value="Un-deafen everyone in your current voice channel.",
                    inline=False)

    embed.add_field(name="`.undeafenme` / `.udme`", value="Un-deafen only yourself.",
                    inline=False)

    embed.add_field(name="`.addexempt` / `.addrole`", value="Add roles that are exempt from being muted",
                    inline=False)

    embed.add_field(name="`.removeexempt` / `.removerole`", value="Remove roles that are exempt from being muted",
                    inline=False)

    embed.add_field(name="Bot not muting everyone?", value="Ask everyone to reconnect to the voice channel.", inline=False)

    embed.add_field(name="_", value="[Join support server](https://discord.gg/8hrhffR6aX)", inline=False)

    if ctx.channel.name == "bot-panel":
        await ctx.send(embed=embed)


async def show_common_error(ctx, embed, e):
    embed.clear_fields()
    embed.add_field(name=f"Something went wrong ({e})", value="[Join support server](https://discord.gg/8hrhffR6aX) for help.")
    await ctx.send(embed=embed)


async def show_permission_error(ctx, embed):
    embed.clear_fields()
    embed.add_field(name=f"No Permission", value="Make sure I have the necessary permissions. If unsure, try giving me the 'administrator' permission or [Join support server](https://discord.gg/8hrhffR6aX)")
    await ctx.send(embed=embed)


# mutes everyone in the current voice channel and un-mutes the bots
@client.command(aliases=["m", "M", "Mute"])
async def mute(ctx):
    # command_name = "mute"
    author = ctx.author  # command author
    embed = discord.Embed(color=discord.Color.red())
    botEmbed = discord.Embed(color=discord.Color.green())

    if ctx.guild:  # check if the msg was in a server's text channel
        if ctx.channel.name == "bot-panel":
            if author.voice:  # check if the user is in a voice channel
                if author.guild_permissions.mute_members:  # check if the user has mute members permission
                    try:
                        no_of_members = 0
                        for member in author.voice.channel.members:  # traverse through the members list in current vc
                            if not member.bot:  # check if member is not a bot
                                if memberCanBeMuted(member):
                                    await member.edit(mute=True)  # mute the non-bot member
                                    no_of_members += 1
                            else:
                                await member.edit(mute=False)  # un-mute the bot member
                                embed.clear_fields()
                                botEmbed.set_author(name=f"Un-muted {member.name}")
                                await ctx.send(embed=botEmbed)
                                # embed.add_field(name="Status", value=f"Un-muted {member.name}")
                        if no_of_members == 0:
                            embed.clear_fields()
                            embed.set_author(name="Muted no one.")
                            # embed.add_field(name="Error", value="Everyone, please reconnect to the voice channel.")
                        else:
                            embed.clear_fields()
                            embed.set_author(name=f"Muted {no_of_members} user(s)")
                            # embed.add_field(name="Status", value=f"Muted {no_of_members} users.")
                        await ctx.send(embed=embed)

                    except discord.Forbidden: # the bot doesn't have the permission to mute
                        await show_permission_error(ctx, embed)
                    except Exception as e:
                        await show_common_error(ctx, embed, e)
                else:
                    embed.clear_fields()
                    embed.add_field(name="Error", value="You don't have the `Mute Members` permission.")
                    await ctx.send(embed=embed)
            else:
                embed.clear_fields()
                embed.add_field(name="Error", value="You must join a voice channel first.")
                await ctx.send(embed=embed)
    else:
        embed.clear_fields()
        embed.add_field(name="Error", value="This does not work in DMs.")
        await ctx.send(embed=embed)


def memberCanBeMuted(member):
    for role in member.roles:
        if role.name in EXEMPT_ROLES:
            return False
    return True


# deafens everyone in the current voice channel
@client.command(aliases=["d", "Deafen"])
async def deafen(ctx):
    command_name = "deafen"
    author = ctx.author
    embed = discord.Embed(color=discord.Color.red())

    if ctx.guild:  # check if the msg was in a server's text channel
        if ctx.channel.name == "bot-panel":
            if author.voice:  # check if the user is in a voice channel
                if author.guild_permissions.deafen_members:  # check if the user has deafen members permission
                    try:
                        no_of_members = 0
                        for member in author.voice.channel.members:  # traverse through the members list in current vc
                            await member.edit(deafen=True)  # deafen the member
                            no_of_members += 1
                        if no_of_members == 0:
                            await ctx.channel.send(f"Everyone, please disconnect and reconnect to the Voice Channel again.")
                        elif no_of_members < 2:
                            await ctx.channel.send(f"Deafened {no_of_members} user in {author.voice.channel}.")
                        else:
                            await ctx.channel.send(f"Deafened {no_of_members} users in {author.voice.channel}.")

                    except discord.Forbidden:
                        await show_permission_error(ctx, embed)
                    except Exception as e:
                        await show_common_error(ctx, embed, e)
                else:
                    await ctx.channel.send("You don't have the `Deafen Members` permission.")
            else:
                await ctx.send("You must join a voice channel first.")
    else:
        await ctx.send("This does not work in DMs.")


# un-mutes everyone in the current voice channel and mutes the bots
@client.command(aliases=["um", "un", "un-mute", "u", "U", "Un", "Um", "Unmute"])
async def unmute(ctx):
    command_name = "unmute"
    author = ctx.author  # command author
    embed = discord.Embed(color=discord.Color.green())
    botEmbed = discord.Embed(color=discord.Color.red())

    if ctx.guild:  # check if the msg was in a server's text channel
        if ctx.channel.name == "bot-panel":
            if author.voice:  # check if the user is in a voice channel
                try:
                    no_of_members = 0
                    for member in author.voice.channel.members:  # traverse through the members list in current vc
                        if not member.bot:  # check if member is not a bot
                            await member.edit(mute=False)  # unmute the non-bot member
                            no_of_members += 1
                        else:
                            await member.edit(mute=True)  # mute the bot member
                            embed.clear_fields()
                            botEmbed.set_author(name=f"Muted {member.name}")
                            await ctx.send(embed=botEmbed)
                            # embed.add_field(name="Status", value=f"Un-muted {member.name}")
                    if no_of_members == 0:
                        embed.clear_fields()
                        embed.set_author(name="Unmuted no one.")
                        # embed.add_field(name="Error", value="Everyone, please reconnect to the voice channel.")
                    else:
                        embed.clear_fields()
                        embed.set_author(name=f"Un-muted {no_of_members} user(s)")
                        # embed.add_field(name="Status", value=f"Muted {no_of_members} users.")
                    await ctx.send(embed=embed)

                except discord.Forbidden: # the bot doesn't have the permission to mute
                    await show_permission_error(ctx, embed)
                except Exception as e:
                    await show_common_error(ctx, embed, e)
            else:
                embed.clear_fields()
                embed.add_field(name="Error", value="You must join a voice channel first.")
                await ctx.send(embed=embed)
    else:
        embed.clear_fields()
        embed.add_field(name="Error", value="This does not work in DMs.")
        await ctx.send(embed=embed)


# un-deafens the user in the current voice channel
@client.command(aliases=["udme", "Undeafenme"])
async def undeafenme(ctx):
    # command_name = "undeafenme"
    author = ctx.author
    embed = discord.Embed(color=discord.Color.red())
    
    if ctx.channel.name == "bot-panel":
        if author.voice:  # check if the user is in a voice channel
            try:
                await author.edit(deafen=False)
                await ctx.send(f"Un-deafened {author.name}.")

            except discord.Forbidden:
                await show_permission_error(ctx, embed)
            except Exception as e:
                await show_common_error(ctx, embed, e)
        else:
            await ctx.send("You must join a voice channel first.")


# un-deafens everyone in the current voice channel
@client.command(aliases=["ud", "Undeafen"])
async def undeafen(ctx):
    # command_name = "undeafen"
    author = ctx.author
    embed = discord.Embed(color=discord.Color.red())

    if ctx.guild:  # check if the msg was in a server's text channel
        if ctx.channel.name == "bot-panel":
            if author.voice:  # check if the user is in a voice channel
                if author.guild_permissions.deafen_members:  # check if the user has deafen members permission
                    try:
                        no_of_members = 0
                        for member in author.voice.channel.members:  # traverse through the members list in current vc
                            await member.edit(deafen=False)  # un-deafen the member
                            no_of_members += 1
                        if no_of_members == 0:
                            await ctx.channel.send(f"Everyone, please disconnect and reconnect to the Voice Channel again.")
                        elif no_of_members < 2:
                            await ctx.channel.send(f"Un-deafened {no_of_members} user in {author.voice.channel}.")
                        else:
                            await ctx.channel.send(f"Un-deafened {no_of_members} users in {author.voice.channel}.")

                    except discord.Forbidden:
                        await show_permission_error(ctx, embed)
                    except Exception as e:
                        await show_common_error(ctx, embed, e)
                else:
                    await ctx.channel.send("You don't have the `Mute Members` permission.")
            else:
                await ctx.send("You must join a voice channel first.")
    else:
        await ctx.send("This does not work in DMs.")

@client.command(aliases=["addexempt","addrole"])
async def addExemptRole(ctx, args):
    if ctx.channel.name == "bot-panel":
        if guildHasRole(ctx.guild, args):
            if (args not in EXEMPT_ROLES):
                EXEMPT_ROLES.append(args)
                saveRoles()
                embed = discord.Embed(color=discord.Color.green())
                embed.clear_fields()
                embed.set_author(name=args + " added to exempt roles")
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(color=discord.Color.red())
                embed.clear_fields()
                embed.add_field(name="Error", value="That role is already exempt")
                await ctx.send(embed=embed)
        else:
            await ctx.send("No role by that name")

@client.command(aliases=["removeexempt","removerole"])
async def removeExemptRole(ctx, args):
    if ctx.channel.name == "bot-panel":
        if args in EXEMPT_ROLES:
            EXEMPT_ROLES.remove(args)
            saveRoles()
            embed = discord.Embed(color=discord.Color.green())
            embed.clear_fields()
            embed.set_author(name=args + " removed for exempt roles")
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(color=discord.Color.red())
            embed.clear_fields()
            embed.add_field(name="Error", value="That role is not exempt")
            await ctx.send(embed=embed)

def saveRoles():
    file = open("exempt_roles.txt", "w")
    for role in EXEMPT_ROLES:
        file.write(role + ",")
    file.close()

def guildHasRole(guild, roleName):
    for role in guild.roles:
        if role.name == roleName:
            return True
    return False

async def mute_with_reaction(user):
    # command_name = "mute_with_reaction"
    try:
        if user.voice:  # check if the user is in a voice channel
            if user.guild_permissions.mute_members:  # check if the user has mute members permission
                for member in user.voice.channel.members:  # traverse through the members list in current vc
                    if not member.bot:  # check if member is not a bot
                        await member.edit(mute=True)  # mute the non-bot member
                    else:
                        await member.edit(mute=False)  # un-mute the bot member
    except Exception as e:
        pass


async def unmute_with_reaction(user):
    # command_name = "unmute_with_reaction"
    try:
        if user.voice:  # check if the user is in a voice channel
            for member in user.voice.channel.members:  # traverse through the members list in current vc
                if not member.bot:  # check if member is not a bot
                    await member.edit(mute=False)  # mute the non-bot member
                else:
                    await member.edit(mute=True)  # un-mute the bot member
    except Exception as e:
        pass


@client.command()
async def stats(ctx):

    guilds = client.guilds
    no_of_guilds = len(guilds)
    no_of_members = 0
    
    for guild in guilds:
        no_of_members = no_of_members + guild.member_count

    embed = discord.Embed(color=discord.Color.blurple())

    embed.set_author(name="MuteAll Stats")
    embed.add_field(name="Used In", value=f"{no_of_guilds} Servers")
    embed.add_field(name="Used By", value=f"{no_of_members} Users")

    await ctx.send(embed=embed)

# hotkey
# @client.command()
# async def a(ctx):
#     while True:
#         if ctx.author.voice.self_mute:
#             await mute(ctx)
#         await asyncio.sleep(1)


# run the bot
client.run(TOKEN)
