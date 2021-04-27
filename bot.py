import discord
from discord.ext import commands
import random

from moderation.hate_speech.core import MLP
from moderation.hate_speech.clf import HateSpeechClassifier, Preprocesser
from data.user.db_handler import UsersDataHandler
from utils.replies import *
from utils.loader import *

import torch
import numpy as np
import logging
import os
import pickle
from datetime import datetime
import sqlite3

def start():
    '''
    Starts the bot
    '''

    print('Starting bot...')

    # set working dir and paths
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    print('Loading database...', end ='')
    conn = sqlite3.connect('data/user/user.db', detect_types=sqlite3.PARSE_DECLTYPES)
    db = UsersDataHandler(conn)
    print('DONE')


    # set up logging
    logger = get_logger()

    # set up classifier
    clf = get_classifier()

    # get replies
    replies = get_replies()


    _prefix = '!'
    bot, client, _client = get_bot_client(_prefix)

    @bot.event
    async def on_ready():
        '''
        Triggers when bot is ready to go
        '''
        print('*** READY ***')
        print('Logged in as')
        print(bot.user.name)
        print(bot.user.id)
        print('------')
        
        return

    @bot.command()
    async def list_commands(ctx):
        '''
        Command that returns currenly supported list of commands
        '''
        available_commands = \
        f'''
        {_prefix}who: Tells you a bit about myself\
        \n{_prefix}warned: Tells you if have already been warned\
        \n{_prefix}sorry: Removes all your warnings for only the first time\
        \n{_prefix}exit [Admin-only]: My cue to leave\
        \n{_prefix}thanks: Makes the bot feel good about itself
        '''
        return await ctx.send(available_commands)

    @bot.command()
    async def who(ctx):
        '''
        Returns some basic information about the bot
        '''
        reply = \
        '''
        {}, I'm Shuddi, a bot that helps keep your channel free of profanity. To know more about me, head over to my GitHub Repository\
        '''.format(random.choice(replies['greet']))
        return await ctx.send(reply)


    @bot.command()
    async def warned(ctx):
        '''
        Returns the level at which the user has been warned
        '''
        warning_level = db.get_warning_level(ctx.message.author)
        if warning_level is None or warning_level == 0:
            reply = f'{ctx.message.author.name}, you have not violated any rules.'

        elif warning_level == 1:
            reply = f'{ctx.message.author.name}, you already have been warned once.'

        else:
            reply = f'{ctx.message.author.name}, you have already been warned twice. Next violation will result in a kick.'

        return await ctx.send(reply)

    @bot.command()
    async def sorry(ctx):
        '''
        Command that lets users strike off their warnings
        '''
        return await ctx.send(on_apology(ctx))

    @bot.command()
    async def thanks(ctx):
        '''
        Command that triggers a 'your're welcome'
        ''' 
        return await ctx.send(on_thanks(ctx))

    def on_thanks(ctx):
        '''
        Triggers when the bot says thanks
        '''
        return random.choice(replies['on_thanks']).format(ctx.message.author.name)

    
    def on_apology(ctx):
        '''
        Handles apology. If a user has apologized within 24 hours, another apology will not be accepted.
        If not, accepts it and strikes off their warnings.
        '''
        author = ctx.message.author

        prev_apology = db.get_prev_apology(author)

        if prev_apology == False:
            # user does not exist in database
            return f'{author.name}, it\'s all good.'

        warning_level = db.get_warning_level(author)

        if warning_level is None or warning_level == 0:
            return f'{author.name}, it\'s all good.'

        if prev_apology is not None:
            hours_since_last_apology = (datetime.now() - prev_apology).total_seconds() / (60 * 60)
        else:
            # user has not apologized ever, so go easy on him.
            hours_since_last_apology = 100

        if hours_since_last_apology >= 24:
            _ = db.reset_warning_level(author)
            _ = db.set_prev_apology(author)
            reply = random.choice(replies['apology_on_n_warning']).format(ctx.message.author.name)

        else:
            reply = random.choice(replies['unaccepted_apology']).format(ctx.message.author.name)

        return reply



    @bot.command()
    @commands.is_owner()
    async def exit(ctx):
        '''
        Shuts down the bot
        '''
        await ctx.send(random.choice(replies['on_exit']))
        await bot.logout()
        

    @bot.event
    async def on_message(message):
        '''
        On every new message sent in the group, checks if it is a command. if so, processes it.
        Also checks if the message is explicit or hateful, if so, issues a warning to the user.
        '''
        channel = message.channel
        try:
            if message.content.startswith(_prefix):
                # if its a command, process commands and return
                return await bot.process_commands(message)
        except discord.ext.commands.errors.CommandNotFound:
            await channel.send('Invalid command. Please use !list_commands to see the currently supported commands.')
            pass

        if message.author.bot:
            # if author is a bot, ignore
            return

        if clf.predict(message.content):
            return await channel.send(await on_hate_speech(message))



    async def on_hate_speech(message):
        '''
        Increases warning level and takes action against repeat offenders
        '''
        db.increase_warning_level(message.author)
        warning_level = db.get_warning_level(message.author)

        if warning_level == 1:
            reply = random.choice(replies['on_1_warning']).format(message.author.name)

        elif warning_level == 2:
            reply = random.choice(replies['on_2_warning']).format(message.author.name)

        else:
            try:
                await message.author.kick(reason='Hateful/profane messages')
                reply = f'User {message.author.name} has been kicked.' 
            except discord.errors.Forbidden as e:
                reply = f'Could not kick {message.author}, this incident will be reported.'
                logger.warning(f'{e}: Bot tried to kick admin {message.author} for hateful messages')

        return reply
  
    try:
        with open('utils/token.pickle', 'rb') as save_file:
            TOKEN = pickle.load(save_file) # token is unique
    except FileNotFoundError:
        print('Token not found, please find your token and store it in utils/token.pickle')
    bot.run(TOKEN)