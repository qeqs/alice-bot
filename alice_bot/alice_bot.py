# coding=utf-8
import json
import logging
import random
from copy import copy

from PIL import Image

from flask import Flask, request

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

sessionStorage = {}
newGameButtons = ['Новая игра']
inGameButtons = ["Ещё", "Хватит"]
deck = {
    '6♠': 6,
    '6♣': 6,
    '6♥': 6,
    '6♦': 6,

    '7♠': 7,
    '7♣': 7,
    '7♥': 7,
    '7♦': 7,

    '8♠': 8,
    '8♣': 8,
    '8♥': 8,
    '8♦': 8,

    '9♠': 9,
    '9♣': 9,
    '9♥': 9,
    '9♦': 9,

    '10♠': 10,
    '10♣': 10,
    '10♥': 10,
    '10♦': 10,

    'T♠': 11,
    'T♣': 11,
    'T♥': 11,
    'T♦': 11,

    'K♠': 4,
    'K♣': 4,
    'K♥': 4,
    'K♦': 4,

    'Д♠': 3,
    'Д♣': 3,
    'Д♥': 3,
    'Д♦': 3,

    'B♠': 2,
    'B♣': 2,
    'B♥': 2,
    'B♦': 2,
}


@app.route("/", methods=['POST'])
def main():
    logging.info('Request: %r', request.json)

    response = {
        "version": request.json['version'],
        "session": request.json['session'],
        "response": {
            "end_session": False
        }
    }

    handle(request.json, response)

    logging.info('Response: %r', response)

    return json.dumps(
        response,
        ensure_ascii=False,
        indent=2
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

        res['response']['text'] = 'Привет! %s' % get_score(user_id)
        res['response']['buttons'] = get_suggests(user_id)
        return

    if req['request']['original_utterance'].lower() in [
        'новая игра',
        'новая'
    ]:
        sessionStorage[user_id]["cards"] = []
        sessionStorage[user_id]["opponent_cards"] = []
        sessionStorage[user_id]['is_started'] = True
        sessionStorage[user_id]['score'] -= 10
        sessionStorage[user_id]['bet'] = 10
        sessionStorage[user_id]['current_deck'] = copy(deck)

        more(user_id)
        more(user_id)
        opponent_more(user_id)
        opponent_more(user_id)
        res['response']['text'] = '%s = %s \n%s' % (your_cards_as_str(sessionStorage[user_id]["cards"]),
                                                    calculate_score(sessionStorage[user_id]["cards"]),
                                                    get_score(user_id))
        res['response']['buttons'] = get_suggests(user_id)
        return

    if sessionStorage[user_id]['is_started']:
        set_suggests(user_id, inGameButtons)

    if req['request']['original_utterance'].lower() in [
        'ещё',
        'еще'
    ]:
        more(user_id)
        res['response']['text'] = '%s = %s \n%s' % (your_cards_as_str(sessionStorage[user_id]["cards"]),
                                                    calculate_score(sessionStorage[user_id]["cards"]),
                                                    get_score(user_id))
        res['response']['buttons'] = get_suggests(user_id)
        return

    if req['request']['original_utterance'].lower() in [
        'хватит',
        'стоп',
        'пас'
    ]:
        process_opponent(user_id)
        text = '%s = %s \n%s \n%s = %s' % (
            your_cards_as_str(), calculate_score(sessionStorage[user_id]["cards"]), get_score(user_id),
            opponent_cards_as_str(), calculate_score(sessionStorage[user_id]["opponent_cards"])
        )
        if calculate_result(user_id):
            sessionStorage[id]['score'] = sessionStorage[id]['bet'] * 2
            text += '\nПобеда:)'
        else:
            text += '\nПоражение:('

        sessionStorage[user_id]['is_started'] = False
        sessionStorage[id]['bet'] = 0
        res['response']['text'] = text
        set_suggests(user_id, newGameButtons)
        res['response']['buttons'] = get_suggests(user_id)
        return

    res['response']['text'] = "Я Вас не поняла"
    res['response']['buttons'] = get_suggests(user_id)


def get_suggests(id):
    session = sessionStorage[id]
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests']
    ]
    return suggests


def set_suggests(id, new_val):
    sessionStorage[id]['suggests'] = new_val


def get_card_img(card):
    img = Image.open("ImageName.jpg")
    pass


def more(id):
    sessionStorage[id]["cards"].append(get_card(get_current_deck(id)))


def opponent_more(id):
    sessionStorage[id]["opponent_cards"].append(get_card(get_current_deck(id)))


def calculate_score(cards):
    score = 0
    aces = 0
    for card in cards:
        score += card.value
        if 'T' in card.key:
            aces += 1
    if score > 21 and aces > 0:
        for i in range(0, aces):
            score -= 10


def your_cards_as_str(id):
    cards = sessionStorage[id]["cards"]
    return 'Your cards: %s' % [card.key for card in cards].__str__()


def opponent_cards_as_str(id):
    cards = sessionStorage[id]["opponent_cards"]
    return 'Opponent cards: %s' % [card.key for card in cards].__str__()


def get_card(deck):
    item = random.choice(deck.items())
    del deck[item.key]
    return item


def get_current_deck(id):
    return sessionStorage[id]['current_deck']


def get_score(id):
    return 'Ваш счет %s' % sessionStorage[id]['score']


def process_opponent(id):
    while calculate_score(sessionStorage[id]["opponent_cards"]) < 17 and \
            len(sessionStorage[id]["opponent_cards"]) < 6:
        opponent_more(id)


def calculate_result(id):
    op_score = calculate_score(sessionStorage[id]["opponent_cards"])
    user_score = calculate_score(sessionStorage[id]["cards"])
    return op_score > 21 or user_score > op_score and user_score <= 21
