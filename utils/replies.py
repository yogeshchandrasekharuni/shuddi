import pickle
from pdb import set_trace


def set_replies():
    replies = dict({
        'greet': [ # for general greetings during !who
            'Namaskaram',
            'Hello',
            'Hi',
            'Namaste',
            'Howdy'
        ],

        'apology_on_0_warning': [ # when user apologizes for nothing
            '{}, you have nothing to apologize for!', 
            '{}, don\'t be!',
            '{}, ah come on, you have no reason to be sorry!'
        ],
        
        'apology_on_n_warning': [ # when user apologizes
            '{}, nevermind! All of your strikes have been wiped off.',
            '{}, that\'s OK! All of your warnings have been removed.',
            '{}, no biggie! All of your warnings have been removed'
        ],

        'unaccepted_apology': [
            '{}, currently, there are no more excuses for your violations.',
            '{}, as of now, your warnings still stand.'
        ],
        
        'on_1_warning': [ # when the first warning has been issued to a user
            '{}, hate-spech and profanity are not tolerated. Consider yourself warned.',
            '{}, this is a warning, hate-speech and profanity will not be taken lightly.'
        ],

        'on_2_warning': [ # when the second and final warning have been issued to a user.
            '{}, you have already been warned once. Another code-violation will lead to a kick.',
            '{}, this is your second warning. Another profane or hateful message will lead to a kick'
        ],

        'on_thanks': [
            '{}, anytime! <3',
            '{}, no biggie <3',
            '{}, don\'t mention it <3'
        ],

        'on_exit': [
            'See ya! :)',
            'Later! :D',
            'Until next time :)'
        ]

    })

    import os
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    with open('replies.pickle', 'wb') as save_file:
        pickle.dump(replies, save_file)


if __name__ == '__main__':
    flag = False
    if flag:
        set_replies()