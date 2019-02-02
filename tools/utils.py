import random
import datetime
import discord
import asyncio
import copy
import inspect
import itertools
import re
from difflib import SequenceMatcher

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

class CannotPaginate(Exception):
    pass

startupLogs = []
logsChannel = 514057242396327964

def color(color=None):
    colors = {
        'blue': 0x0000ff,
        'pink1': 0xcc99ff,
        'pink2': 0xf3a0d5,
        'pink3': 0xeb61b9,
        'red': 0xe60502,
        'aqua': 0x02e3e6,
        'green1': 0x41e641,
        'yellow': 0xf4de4e,
        'purple': 0x954ef4,
        'green2': 0x92c26e
    }
    values = list(colors.values())

    def getRandom():
        return random.choice(values)

    randomX = False

    if color is None:
        randomX = True 
    
    if not randomX:
        try:
            return colors[color]
        except KeyError:
            randomX = True 
    
    if randomX:
        return getRandom()

# Set embed's footer
def footer(embed, ctx=None, text=None, icon=None, user=None):

    embed.timestamp = datetime.datetime.utcnow()
    if text != None:
        text = text
    else:
        try:
            if ctx != None:
                text = f"{ctx.author.name}#{ctx.author.discriminator}"
            else:
                text = f"{user.name}#{user.discriminator}"
        except:
            pass 

    if icon != None:
        icon = icon
    else:
        try:
            if ctx != None:
                icon = ctx.author.avatar_url 
            else:
                if user is None:
                    icon = None 
                else:
                    icon = user.avatar_url
        except:
            icon = None 
            
    embed.set_footer(text=text, icon_url=icon)

# A shortened version of the discord embed
def embed(ctx=None, title=None, description=None, fields=None, customFooter=False, customThumbnail=None, customColor=None, image=None):
    """
    fields is a list of dictionaries

    n = Title 
    v = Value 
    If inline is not set then the default value will be false
    [
        {"n": "Rewind", "v": "Time", "inline": True},
        ...
    ]
    """

    e = discord.Embed(title=title, description=description)
    if customColor is None:
        e.color = color()
    else:
        e.color = color(customColor)
    
    if fields != None:
        index = 0
        # Please fix the code below, There's nothing wrong with it, it's just messy and I'm sure that's not the right way to do it.
        for field in fields:
            session = []
            for key, value in field.items():
                session.append(key)

                if key == "n":
                    name = value 
                
                if key == "v":
                    xValue = value 
                
                if key == "inline":
                    inline = value 
                
                if not "inline" in session:
                    inline = False
                
            e.add_field(name=f"{name}", value=xValue, inline=inline)
    
    if not customFooter:
        footer(e, ctx)
    
    if image is None:
        try:
            if customThumbnail is None:
                e.set_thumbnail(url=ctx.author.avatar_url)
            else:
                e.set_thumbnail(url=customThumbnail)
        except:
            pass 
    else:
        e.set_image(url=image)
    return e

def returnPrefix(ctx=None):
    default = "!"
    return default
    # Get prefix from database here if you want

async def usage(ctx, arguments, example, description=None):
    prefix = returnPrefix(ctx)
    args = [f"<{arg}>" for arg in arguments]
    arguments = " ".join(args)
    example = " ".join(example)
    command = ctx.command.qualified_name

    fields = [
        {"n": "Proper Usage", "v":f"{prefix}{command} {arguments}"},
        {"n": "Example", "v":f"{prefix}{command} {example}"},
    ]
    if description != None:
        fields.append({"n": "Description", "v":description})

    e = embed(title="Wrong Usage", fields=fields, ctx=ctx)
    await ctx.send(embed=e)

async def error(ctx, error, message="Please send this message to the developer"):
    e = embed(ctx, title=f"Error in command : {ctx.command}", description=f"```{error}```", customColor="red", customFooter=True)
    footer(e, ctx, message)
    await ctx.send(embed=e)

class Paginator:
    # Original work Copyright (c) 2015 Rapptz (https://github.com/Rapptz/RoboDanny)
    # Modified work Copyright (c) 2017 Perry Fraser
    #
    # Licensed under the MIT License. https://opensource.org/licenses/MIT

    # Stolen line for line from paginator.py in R. Danny's code
    # Added formatting and lots of blocking of inspections
    def __init__(self, ctx, *, embeds):
        self.bot = ctx.bot
        self.embeds = embeds
        self.message = ctx.message
        self.channel = ctx.channel
        self.author = ctx.author
        pages = len(self.embeds)
        self.maximum_pages = pages
        self.paginating = len(embeds) > 1
        self.reaction_emojis = [
            ('\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}',
             self.first_page),
            ('\N{BLACK LEFT-POINTING TRIANGLE}', self.previous_page),
            ('\N{BLACK RIGHT-POINTING TRIANGLE}', self.next_page),
            ('\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}',
             self.last_page),
            ('\N{INPUT SYMBOL FOR NUMBERS}', self.numbered_page)
        ]

        if ctx.guild is not None:
            self.permissions = self.channel.permissions_for(ctx.guild.me)
        else:
            self.permissions = self.channel.permissions_for(ctx.bot.user)

        if not self.permissions.embed_links:
            raise CannotPaginate('Bot does not have embed links permission.')

        if not self.permissions.send_messages:
            raise CannotPaginate('Bot cannot send messages.')

        if self.paginating:
            # verify we can actually use the pagination session
            if not self.permissions.add_reactions:
                raise CannotPaginate(
                    'Bot does not have add reactions permission.')

            if not self.permissions.read_message_history:
                raise CannotPaginate(
                    'Bot does not have Read Message History permission.')

    async def show_page(self, page, *, first=False):
        # noinspection PyAttributeOutsideInit
        self.current_page = page
        embed = copy.copy(self.embeds[page - 1])
        p = []

        if self.maximum_pages > 1:
            text = f'Page {page}/{self.maximum_pages}'

            embed.set_footer(text=text)

        if not self.paginating:
            return await self.channel.send(embed=embed)

        if not first:
            return await self.message.edit(embed=embed)

        p.append('')
        p.append('Navigate with the buttons below')
        embed.description = '' if embed.description == discord.Embed.Empty \
            else embed.description
        embed.description += '\n'.join(p)
        self.message = await self.channel.send(embed=embed)

        await self.add_rest_reactions()

    async def add_rest_reactions(self):
        await self.message.remove_reaction('🔣', self.message.guild.me)
        for (reaction, _) in self.reaction_emojis:
            if self.maximum_pages == 2 and reaction in ('\u23ed', '\u23ee'):
                # no |<< or >>| buttons if we only have two pages
                # we can't forbid it if someone ends up using it but remove
                # it from the default set
                continue

            await self.message.add_reaction(reaction)

    async def checked_show_page(self, page):
        if page != 0 and page <= self.maximum_pages:
            await self.show_page(page)

    async def first_page(self):
        """goes to the first page"""
        await self.show_page(1)

    async def last_page(self):
        """goes to the last page"""
        await self.show_page(self.maximum_pages)

    async def next_page(self):
        """goes to the next page"""
        await self.checked_show_page(self.current_page + 1)

    async def previous_page(self):
        """goes to the previous page"""
        await self.checked_show_page(self.current_page - 1)

    async def show_current_page(self):
        if self.paginating:
            await self.show_page(self.current_page)

    async def numbered_page(self):
        """lets you type a page number to go to"""
        # noinspection PyListCreation
        to_delete = []
        to_delete.append(
            await self.channel.send('What page do you want to go to?')
        )

        def message_check(m):
            return m.author == self.author and \
                   self.channel == m.channel and \
                   m.content.isdigit()

        try:
            msg = await self.bot.wait_for('message', check=message_check,
                                          timeout=30.0)
        except asyncio.TimeoutError:
            to_delete.append(await self.channel.send('Took too long.'))
            await asyncio.sleep(5)
        else:
            page = int(msg.content)
            to_delete.append(msg)
            if page != 0 and page <= self.maximum_pages:
                await self.show_page(page)
            else:
                to_delete.append(await self.channel.send(
                    f'Invalid page given. ({page}/{self.maximum_pages})'))
                await asyncio.sleep(5)

        # noinspection PyBroadException
        try:
            await self.channel.delete_messages(to_delete)
        except Exception:
            pass

    async def show_help(self):
        """shows this message"""
        messages = ['Welcome to the interactive paginator!\n',
                    'This interactively allows you to see pages '
                    'of text by navigating with '
                    'reactions. They are as follows:\n']

        for (emoji, func) in self.reaction_emojis:
            messages.append(f'{emoji} {func.__doc__}')

        embed = discord.Embed()

        embed.description = '\n'.join(messages)
        embed.clear_fields()
        embed.set_footer(
            text=f'We were on page {self.current_page} before this message.')
        await self.message.edit(embed=embed)

        async def go_back_to_current_page():
            await asyncio.sleep(60.0)
            await self.show_current_page()

        self.bot.loop.create_task(go_back_to_current_page())

    async def stop_pages(self):
        """stops the interactive pagination session"""
        await self.message.delete()
        self.paginating = False

    def react_check(self, reaction, user):
        if user is None or user.id != self.author.id:
            return False

        if reaction.message.id != self.message.id:
            return False

        # if reaction.emoji == '🔣':
        #     self.match = self.add_rest_reactions
        #     return True

        for (emoji, func) in self.reaction_emojis:
            if reaction.emoji == emoji:
                # noinspection PyAttributeOutsideInit
                self.match = func
                return True
        return False

    async def paginate(self):
        """Actually paginate the entries and
        run the interactive loop if necessary."""
        first_page = self.show_page(1, first=True)
        if not self.paginating:
            await first_page
        else:
            # allow us to react to reactions right away if we're paginating
            self.bot.loop.create_task(first_page)

        while self.paginating:
            try:
                reaction, user = await self.bot.wait_for('reaction_add',
                                                         check=self.react_check,
                                                         timeout=120.0)
            except asyncio.TimeoutError:
                self.paginating = False
                # noinspection PyBroadException
                try:
                    await self.message.clear_reactions()
                except:
                    pass
                finally:
                    break

            # noinspection PyBroadException
            try:
                await self.message.remove_reaction(reaction, user)
            except:
                pass  # can't remove it so don't bother doing so

            await self.match()