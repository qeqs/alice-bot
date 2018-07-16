# coding=utf-8
import json
from copy import deepcopy

import pytest
from alice_bot import alice_bot as ab


@pytest.fixture()
def req_start_fixture():
    return {
        "meta": {
            "client_id": "Developer Console",
            "locale": "ru-RU",
            "timezone": "UTC"
        },
        "request": {
            "command": u"Новая игра",
            "original_utterance": u"Новая игра",
            "type": "SimpleUtterance"
        },
        "session": {
            "message_id": 1,
            "new": True,
            "session_id": "b154e9f8-e3852c95-88474681-c6e32",
            "skill_id": "ec15948b-635d-41f3-b763-34042b34ed62",
            "user_id": "376BC52061F8425EB80BE3249582AD54B532B9176DCFD35634A2F20593FAB44F"
        },
        "version": "1.0"
    }


@pytest.fixture()
def req_new_game_fixture(req_start_fixture):
    req = deepcopy(req_start_fixture)
    req['session']['new'] = False
    yield req


@pytest.fixture()
def req_more_fixture(req_new_game_fixture):
    req = deepcopy(req_new_game_fixture)
    req['request']['original_utterance'] = u"Еще"
    req['request']['command'] = u"Еще"
    yield req


@pytest.fixture()
def req_enough_fixture(req_more_fixture):
    req = deepcopy(req_more_fixture)
    req['request']['original_utterance'] = u"Хватит"
    req['request']['command'] = u"Хватит"
    yield req


@pytest.fixture()
def client():
    ab.app.config['TESTING'] = True
    client = ab.app.test_client()
    return client


def test_game(client, req_start_fixture, req_new_game_fixture, req_more_fixture,
              req_enough_fixture):
    headers = {'Content-Type': 'application/json'}

    resp = client.post('/', data=json.dumps(req_start_fixture), headers=headers)
    print('\n'+json.loads(resp.data,
                     encoding='utf8'
                     )['response']['text'])

    resp = client.post('/', data=json.dumps(req_new_game_fixture), headers=headers)
    print(json.loads(resp.data,
                     encoding='utf8'
                     )['response']['text'])

    resp = client.post('/', data=json.dumps(req_more_fixture), headers=headers)
    print(json.loads(resp.data,
                     encoding='utf8'
                     )['response']['text'])

    resp = client.post('/', data=json.dumps(req_enough_fixture), headers=headers)
    print(json.loads(resp.data,
                     encoding='utf8'
                     )['response']['text'])
