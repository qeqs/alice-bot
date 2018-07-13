# coding=utf-8
from __future__ import unicode_literals
import json
import logging
import random
from copy import copy

from flask import Flask, request

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

sessionStorage = {}
newGameButtons = ['Новая игра']
inGameButtons = ['Ещё', 'Хватит']
deck = {
    u'6 пик': 6,
    u'6 крести': 6,
    u'6 черви': 6,
    u'6 буби': 6,

    u'7 пик': 7,
    u'7 крести': 7,
    u'7 черви': 7,
    u'7 буби': 7,

    u'8 пик': 8,
    u'8 крести': 8,
    u'8 черви': 8,
    u'8 буби': 8,

    u'9 пик': 9,
    u'9 крести': 9,
    u'9 черви': 9,
    u'9 буби': 9,

    u'10 пик': 10,
    u'10 крести': 10,
    u'10 черви': 10,
    u'10 буби': 10,

    u'Туз пик': 11,
    u'Туз крести': 11,
    u'Туз черви': 11,
    u'Туз буби': 11,

    u'Король пик': 4,
    u'Король крести': 4,
    u'Король черви': 4,
    u'Король буби': 4,

    u'Дама пик': 3,
    u'Дама крести': 3,
    u'Дама черви': 3,
    u'Дама буби': 3,

    u'Валет пик': 2,
    u'Валет крести': 2,
    u'Валет черви': 2,
    u'Валет буби': 2,
}


@app.route('/', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)

    response = {
        'version': request.json['version'],
        'session': request.json['session'],
        'response': {
            'end_session': False
        }
    }

    handle(request.json, response)

    logging.info('Response: %r', response)

    return json.dumps(
        response,
        ensure_ascii=False,
        indent=2,
        encoding='utf-8'
    )


def handle(req, res):
    user_id = req['session']['user_id']
    if req['session']['new']:
        sessionStorage[user_id] = {
            'suggests': newGameButtons,
            'score': 100,
            'bet': 0,
            'is_started': False,
            'cards': [],
            'current_deck': copy(deck),
            'opponent_cards': []
        }

        res['response']['text'] = u'Привет! %s' % get_score(user_id)
        res['response']['buttons'] = get_suggests(user_id)
        return

    if req['request']['original_utterance'].lower() in [
        'новая игра',
        'новая'
    ]:
        sessionStorage[user_id]['cards'] = []
        sessionStorage[user_id]['opponent_cards'] = []
        sessionStorage[user_id]['is_started'] = True
        sessionStorage[user_id]['score'] -= 10
        sessionStorage[user_id]['bet'] = 10
        sessionStorage[user_id]['current_deck'] = copy(deck)

        more(user_id)
        more(user_id)
        opponent_more(user_id)
        opponent_more(user_id)
        res['response']['text'] = u'%s = %s \n%s' % (your_cards_as_str(user_id),
                                                     calculate_score(sessionStorage[user_id]['cards']),
                                                     get_score(user_id))
        set_suggests(user_id, inGameButtons)
        res['response']['buttons'] = get_suggests(user_id)
        return

    if req['request']['original_utterance'].lower() in [
        'ещё',
        'еще'
    ]:
        more(user_id)
        res['response']['text'] = u'%s = %s \n%s' % (your_cards_as_str(user_id),
                                                     calculate_score(sessionStorage[user_id]['cards']),
                                                     get_score(user_id))
        res['response']['buttons'] = get_suggests(user_id)
        return

    if req['request']['original_utterance'].lower() in [
        'хватит',
        'стоп',
        'пас'
    ]:
        process_opponent(user_id)
        text = u'%s = %s \n%s \n%s = %s' % (
            your_cards_as_str(user_id), calculate_score(sessionStorage[user_id]['cards']), get_score(user_id),
            opponent_cards_as_str(user_id), calculate_score(sessionStorage[user_id]['opponent_cards'])
        )
        if calculate_result(user_id):
            sessionStorage[user_id]['score'] = sessionStorage[user_id]['bet'] * 2
            text += u'\nПобеда:)'
        else:
            text += u'\nПоражение:('

        sessionStorage[user_id]['is_started'] = False
        sessionStorage[user_id]['bet'] = 0
        res['response']['text'] = text
        set_suggests(user_id, newGameButtons)
        res['response']['buttons'] = get_suggests(user_id)
        return

    res['response']['text'] = u'Я Вас не поняла'
    res['response']['buttons'] = get_suggests(user_id)


def get_suggests(usr_id):
    session = sessionStorage[usr_id]
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests']
    ]
    return suggests


def set_suggests(usr_id, new_val):
    sessionStorage[usr_id]['suggests'] = new_val


def more(usr_id):
    sessionStorage[usr_id]['cards'].append(get_card(get_current_deck(usr_id)))


def opponent_more(usr_id):
    sessionStorage[usr_id]['opponent_cards'].append(get_card(get_current_deck(usr_id)))


def calculate_score(cards):
    score = 0
    aces = 0
    for card in cards:
        score += card[1]
        if 'T' in card[0]:
            aces += 1
    if score > 21 and aces > 0:
        for i in range(0, aces):
            score -= 10
    return score


def your_cards_as_str(usr_id):
    cards = sessionStorage[usr_id]['cards']
    return u'Ваши карты: %s' % [card[0] for card in cards]


def opponent_cards_as_str(usr_id):
    cards = sessionStorage[usr_id]['opponent_cards']
    return u'Карты противника: %s' % [card[0] for card in cards]


def get_card(deck):
    item = random.choice(deck.items())
    del deck[item[0]]
    return item


def get_current_deck(usr_id):
    return sessionStorage[usr_id]['current_deck']


def get_score(usr_id):
    return u'Ваш счет %s' % sessionStorage[usr_id]['score']


def process_opponent(usr_id):
    while calculate_score(sessionStorage[usr_id]['opponent_cards']) < 17 and \
            len(sessionStorage[usr_id]['opponent_cards']) < 6:
        opponent_more(usr_id)


def calculate_result(usr_id):
    op_score = calculate_score(sessionStorage[usr_id]['opponent_cards'])
    user_score = calculate_score(sessionStorage[usr_id]['cards'])
    return op_score > 21 or op_score < user_score <= 21
