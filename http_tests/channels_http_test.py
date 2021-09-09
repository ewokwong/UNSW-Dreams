import pytest
import requests
import json
from src.config import url
from src.other import SECRET
import jwt

AuID    = 'auth_user_id'
uID     = 'u_id'
cID     = 'channel_id'
allMems = 'all_members'
Name    = 'name'
dmName  = 'dm_name'
fName   = 'name_first'
lName   = 'name_last'
chans   = 'channels'
token   = 'token'
dmID    = 'dm_id'
handle  = 'handle_string'

#* Fixture that returns a JWT with invalid u_id and session_id
@pytest.fixture
def invalid_token():
    return jwt.encode({'session_id': -1, 'user_id': -1}, SECRET, algorithm='HS256')

#* Fixture that clears and registers the first user
@pytest.fixture
def user1():
    requests.delete(f"{url}clear/v1")    
    response = requests.post(f"{url}auth/register/v2", json={
        "email": "first@gmail.com",
        "password": "password",
        "name_first": "User",
        "name_last": "1"
    })
    return response.json()

#* Fixture that registers a second user
@pytest.fixture
def user2():
    response = requests.post(f"{url}auth/register/v2", json={
        "email": "second@gmail.com",
        "password": "password",
        "name_first": "User",
        "name_last": "2"
    })
    return response.json()

#* Fixture that registers a third user
@pytest.fixture
def user3():
    response = requests.post(f"{url}auth/register/v2", json={
        "email": "third@gmail.com",
        "password": "password",
        "name_first": "User",
        "name_last": "3"
    })
    return response.json()

#* Fixture that registers a fourth user
@pytest.fixture
def user4():
    response = requests.post(f"{url}auth/register/v2", json={
        "email": "fourth@gmail.com",
        "password": "password",
        "name_first": "User",
        "name_last": "4"
    })
    return response.json()

def test_http_channels_create(user1, user2):
    #* This test is structured identically to test_channels_create in tests/channels_test.py
    cResponse = requests.post(f"{url}channels/create/v2", json={
        "token": user1[token],
        "name": "Oogway",
        "is_public": True
    })
    chanOne = cResponse.json()
    responseUser1 = requests.get(f"{url}channels/list/v2", params = {'token': user1[token]})
    assert responseUser1.json() == {
        'channels': [{
            cID: chanOne[cID],
            Name: 'Oogway'
        }]
    }
    assert requests.get(f"{url}channels/listall/v2", params = {'token': user1[token]}).json() == {
        'channels': [{
            cID: chanOne[cID],
            Name: 'Oogway'
        }]
    }
    assert requests.get(f"{url}channels/listall/v2", params = {'token': user2[token]}).json() == {
        'channels': [{
            cID: chanOne[cID],
            Name: 'Oogway'
        }]
    }
    assert requests.get(f"{url}channels/list/v2", params = {'token': user2[token]}).json() == {
        'channels': []
    }

    assert requests.post(f"{url}channels/create/v2", json={
        "token": user1[token],
        "name": "abcdefghijklmnopqrstuvwxyz",
        "is_public": True
    }).status_code == 400

#* Test that for valid inputs, all the channels the user is part of are listed
def test_http_channels_list_valid(user1, user2):
    cResponse = requests.post(f"{url}channels/create/v2", json={
        "token": user1[token],
        "name": "Oogway",
        "is_public": True
    })

    channel = cResponse.json()
    responseUser1 = requests.get(f"{url}channels/list/v2", params = {'token': user1[token]})

    assert responseUser1.json() == {
        'channels': [{
            cID: channel[cID],
            Name: 'Oogway'
        }]
    }

    responseUser2 = requests.get(f"{url}channels/list/v2", params = {'token': user2[token]})

    assert responseUser2.json() == {
        'channels': []
    }

#* Test that for valid inputs, all channels are listed - even if the user is not in them
def test_http_channels_listall_valid(user1, user2):
    cResponse = requests.post(f"{url}channels/create/v2", json={
        "token": user1[token],
        "name": "Oogway",
        "is_public": True
    })
    channel = cResponse.json()

    responseUser1 = requests.get(f"{url}channels/listall/v2", params = {'token': user1[token]})

    assert responseUser1.json() == {
        'channels': [{
            cID: channel[cID],
            Name: 'Oogway'
        }]
    }

    responseUser2 = requests.get(f"{url}channels/listall/v2", params = {'token': user2[token]})

    assert responseUser2.json() == {
        'channels': [{
            cID: channel[cID],
            Name: 'Oogway'
        }]
    }

#* Test that private channels are listed in the return
def test_http_channels_listall_private(user1, user2):
    cResponse = requests.post(f"{url}channels/create/v2", json={
        "token": user1[token],
        "name": "NEZ",
        "is_public": False
    })
    channel = cResponse.json()

    responseUser1 = requests.get(f"{url}channels/listall/v2", params = {'token': user1[token]})

    assert responseUser1.json() == {
        'channels': [{
            cID: channel[cID],
            Name: 'NEZ'
        }]
    }

    responseUser2 = requests.get(f"{url}channels/listall/v2", params = {'token': user2[token]})

    assert responseUser2.json() == {
        'channels': [{
            cID: channel[cID],
            Name: 'NEZ'
        }]
    }

#* Tests if an invalid token correctly raises an AccessError
def test_http_channels_list_invalid_token(invalid_token):
    response = requests.get(f"{url}channels/list/v2", params = {'token': invalid_token})
    assert response.status_code == 403

#* Tests if an invalid token correctly raises an AccessError
def test_http_channels_listall_valid_invalid_token(invalid_token):
    response = requests.get(f"{url}channels/listall/v2", params = {'token': invalid_token})
    assert response.status_code == 403