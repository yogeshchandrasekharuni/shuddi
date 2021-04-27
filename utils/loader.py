import discord
from discord.ext import commands
import random

from moderation.hate_speech.core import MLP
from moderation.hate_speech.clf import HateSpeechClassifier, Preprocesser
from data.user.db_handler import UsersDataHandler
from utils.replies import *

import torch
import numpy as np
import logging
import os
import pickle
from datetime import datetime
import sqlite3

PATH = 'moderation/hate_speech/'
intents = discord.Intents.default()
intents.members = True

def get_classifier():
    '''
    Loads the hate-speech classifier
    '''
    print('Loading classifier...', end ='')
    mlp = MLP() # load the classifier implementation and load the clf
    MODEL_PATH = PATH + 'data/mlp_model_state_dict.pth'
    pp = Preprocesser(dependencies_path = PATH + 'data/dependencies_24_4.pickle')
    mlp.load_state_dict(torch.load(MODEL_PATH))
    mlp.eval()
    clf = HateSpeechClassifier(clf = mlp, pp = pp)
    print('DONE')
    return clf

def get_replies():
    print('Loading replies...', end='')
    with open('utils/replies.pickle', 'rb') as save_file:
        replies = pickle.load(save_file)
        print('DONE')
        return replies


def get_bot_client(_prefix):
    '''
    Initiates bot and client classes
    '''
    bot = commands.Bot(command_prefix=_prefix, description='''Shuddi, a bot that will keep your discord channel free of profanity!''', intents=intents)
    client = commands.Bot(command_prefix='')
    _client = discord.Client()
    return bot, client, _client


def get_logger():
    '''
    Sets up logging
    '''
    _fpath = 'logs/' + datetime.now().strftime('%Y_%m_%d.log')
    print(f'Logging to {_fpath}...')
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename=_fpath, encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)
    return logger