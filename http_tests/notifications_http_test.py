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
ownMems = 'owner_members'
notifs  = 'notifications'
nMess   = 'notification_message'
thumbsUp = 1
mID = 'message_id'

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

#* Fixture that returns a JWT with invalid u_id and session_id
@pytest.fixture
def invalid_token():
    return jwt.encode({'session_id': -1, 'user_id': -1}, SECRET, algorithm='HS256')

def test_http_notifications_get_in_channels(user1, user2, user3, user4):
    #* This test is structured identically to test_notifications_get_in_channels in tests/notifications_test.py
    c1 = requests.post(f"{url}channels/create/v2", json={
        "token": user1[token],
        "name": "TrumpPence",
        "is_public": True
    })
    requests.post(f"{url}channel/invite/v2", json={
        "token": user1[token],
        "channel_id": c1.json()[cID],
        "u_id": user2[AuID]
    })
    notifFound = False
    for notif in requests.get(f"{url}notifications/get/v1", params={
        "token": user2[token]
    }).json()[notifs]:
        if notif[nMess] == "user1 added you to TrumpPence":
            notifFound = True
    assert notifFound is True
    requests.post(f"{url}message/send/v2", json={
        "token": user2[token],
        "channel_id": c1.json()['channel_id'],
        "message": "Hello @user1"
    })
    notifFound = False
    for notif in requests.get(f"{url}notifications/get/v1", params={
        "token": user1[token]
    }).json()[notifs]:
        if notif[nMess] == f"user2 tagged you in TrumpPence: Hello @user1":
            notifFound = True
    assert notifFound is True

    i = 0
    while i < 22:
        requests.post(f"{url}message/send/v2", json={
            "token": user1[token],
            "channel_id": c1.json()['channel_id'],
            "message": "Hi @user2"
        })
        i += 1
    notifFound = False
    for notif in requests.get(f"{url}notifications/get/v1", params={
        "token": user2[token]
    }).json()[notifs]:
        if notif[nMess] == "user1 added you to TrumpPence":
            notifFound = True
    assert notifFound is False

    requests.post(f"{url}message/send/v2", json={
        "token": user1[token],
        "channel_id": c1.json()['channel_id'],
        "message": "Dooo dooo dooo dooo @user2"
    })
    notifFound = False
    for notif in requests.get(f"{url}notifications/get/v1", params={
        "token": user2[token]
    }).json()[notifs]:
        if notif[nMess] == "user1 tagged you in TrumpPence: Dooo dooo dooo dooo ":
            notifFound = True
    assert notifFound is True

    requests.post(f"{url}message/send/v2", json={
        "token": user1[token],
        "channel_id": c1.json()['channel_id'],
        "message": "@Joe_Biden"
    })
    notifFound = False
    for notif in requests.get(f"{url}notifications/get/v1", params={
        "token": user2[token]
    }).json()[notifs]:
        if notif[nMess] == "user1 tagged you in TrumpPence: @Joe_Biden":
            notifFound = True
    assert notifFound is False

def test_http_notifications_dms_added(user1, user2, user3):
    #Create two dm's 
    result = requests.post(f"{url}dm/create/v1", json={
        "token": user1[token],
        "u_ids": [user2[AuID]]
    })
    dm_0 = result.json()
    
    result_2 = requests.post(f"{url}dm/create/v1", json={
        "token": user1[token],
        "u_ids": [user3[AuID]]
    })
    dm_1 = result_2.json()
    
    #Test 1: Notif is received when dm is initially created 
    response = requests.get(f"{url}notifications/get/v1", params={
        "token": user2[token]
    })
    notifs0 = response.json() 
    
    assert {
        cID : -1,
        dmID: dm_0[dmID],
        nMess : f"user1 added you to user1, user2",
    } in notifs0['notifications']

    #Test 2: Notif is received when user3 is invited to dm_0 
    requests.post(f"{url}dm/invite/v1", json={
        "token": user1[token],
        dmID: dm_0[dmID],
        uID: user3[AuID],
    })
    
    #Check user 3 notifs 
    response_2 = requests.get(f"{url}notifications/get/v1", params={
        "token": user3[token]
    })
    notifs1 = response_2.json() 
    
    assert {
        cID : -1,
        dmID: dm_0[dmID],
        nMess : f"user1 added you to user1, user2",
    } in notifs1['notifications']
    
    #Test 3: Check that user 3 still has dm_1 notif still in after being invited 
    assert {
        cID : -1,
        dmID: dm_1[dmID],
        nMess : f"user1 added you to user1, user3",
    } in notifs1['notifications']
    
#* Tests that people can be tagged in messages in DMs
def test_http_valid_dm_tag(user1, user2):
    dmResponse = requests.post(f"{url}dm/create/v1", json={
        "token": user1[token],
        "u_ids": [user2[AuID]]
    })
    dm1 = dmResponse.json()

    requests.post(f"{url}message/senddm/v1", json={
        token: user1[token],
        dmID: dm1[dmID],
        'message': 'Hi @user2'
    })

    requests.post(f"{url}message/senddm/v1", json={
        token: user2[token],
        dmID: dm1[dmID],
        'message': 'Hi @user1'
    })

    response0 = requests.get(f"{url}notifications/get/v1", params={
        "token": user1[token]
    })
    notifs0 = response0.json()
    response1 = requests.get(f"{url}notifications/get/v1", params={
        "token": user2[token]
    })
    notifs1 = response1.json()

    assert len(notifs0['notifications']) == 1
    assert len(notifs1['notifications']) == 2

#* Test that the notification message displayed when being tagged in a dm is only the first 20 characters
def test_http_valid_dm_20_chars(user1, user2):
    dmResponse = requests.post(f"{url}dm/create/v1", json={
        "token": user1[token],
        "u_ids": [user2[AuID]]
    })
    dm1 = dmResponse.json()
    message = '@user2' + ' ' + f"{'a'*25}"
    requests.post(f"{url}message/senddm/v1", json={
        token: user1[token],
        dmID: dm1[dmID],
        'message': message
    })
    response1 = requests.get(f"{url}notifications/get/v1", params={
        "token": user2[token]
    })
    notifs = response1.json()

    assert {
        cID : -1,
        dmID: dm1[dmID],
        nMess : f"user1 tagged you in user1, user2: {message[0:20]}",
    } in notifs['notifications']

#* Assert that users cannot be tagged in dms they are not in
def test_http_dm_no_tag(user1, user2, user3):
    dmResponse = requests.post(f"{url}dm/create/v1", json={
        "token": user1[token],
        "u_ids": [user2[AuID]]
    })
    dm1 = dmResponse.json()
    requests.post(f"{url}message/senddm/v1", json={
        token: user1[token],
        dmID: dm1[dmID],
        'message': 'Hi @user3'
    })
    response1 = requests.get(f"{url}notifications/get/v1", params={
        "token": user3[token]
    })
    notifs = response1.json()

    assert notifs['notifications'] == []

#* When getting more than 20 notifs, check if only 20 of the most recent ones are displayed
def test_http_dm_20_notifs(user1, user2):
    dmResponse = requests.post(f"{url}dm/create/v1", json={
        "token": user1[token],
        "u_ids": [user2[AuID]]
    })
    dm1 = dmResponse.json()
    tagMessage = '@user2'
    for nNum in range(21):
        message = str(nNum) + ' ' + tagMessage
        requests.post(f"{url}message/senddm/v1", json={
        token: user1[token],
        dmID: dm1[dmID],
        'message': message
    })

    response = requests.get(f"{url}notifications/get/v1", params={
        "token": user2[token]
    })
    notifs = response.json()

    assert len(notifs['notifications']) == 20
    assert {
        cID : -1,
        dmID: dm1[dmID],
        nMess : "user1 tagged you in user1, user2: 0 @user2" 
    } not in notifs['notifications']

#* When editing a dm message, the user is tagged
def test_http_dm_edit_notif(user1, user2):
    dmResponse = requests.post(f"{url}dm/create/v1", json={
        "token": user1[token],
        "u_ids": [user2[AuID]]
    })
    dm1 = dmResponse.json()

    mResponse = requests.post(f"{url}message/senddm/v1", json={
        token: user2[token],
        dmID: dm1[dmID],
        'message': 'Hi'
    })
    message = mResponse.json()

    requests.put(f"{url}message/edit/v2", json={
        "token": user2[token],
        "message_id": message['message_id'],
        "message": "Hi @user1"
    })

    nResponse = requests.get(f"{url}notifications/get/v1", params={
        "token": user1[token]
    })
    notifs = nResponse.json()

    assert {
        cID : -1,
        dmID: dm1[dmID],
        nMess : f"user2 tagged you in user1, user2: Hi @user1",
    } in notifs['notifications']


#Test that people in a channel who have a message reacted to will get a notif 
def test_http_channel_react_notif(user1, user2):
    channelResponse = requests.post(f"{url}channels/create/v2", json={
        "token": user1[token],
        "name": "Hello",
        "is_public": True
    })
    c1 = channelResponse.json()
    
    requests.post(f"{url}channel/invite/v2", json={
        "token": user1[token],
        "channel_id": c1[cID],
        "u_id": user2[AuID],
    })
    
    messageResponse = requests.post(f"{url}message/send/v2", json={
        token: user1[token],
        cID: c1[cID],
        'message': 'Hi @user2'
    })
    m1 = messageResponse.json()

    requests.post(f"{url}message/react/v1", json={
        token: user2[token],
        mID: m1[mID],
        'react_id': thumbsUp
    })
    
    response = requests.get(f"{url}notifications/get/v1", params={
        "token": user1[token]
    })
    
    notifs = response.json()
    assert {
        cID: c1[cID],
        dmID: -1, 
        nMess: "user2 reacted to your message in Hello"
    } in notifs['notifications']
    assert len(notifs['notifications']) == 1
    

#Test that people in a DM who get their message reacted to will get a notif 
def test_http_dm_react_notif(user1,user2):

    dmResponse = requests.post(f"{url}dm/create/v1", json={
        "token": user1[token],
        "u_ids": [user2[AuID]]
    })
    dm1 = dmResponse.json()

    messageResponse = requests.post(f"{url}message/senddm/v1", json={
        token: user1[token],
        dmID: dm1[dmID],
        'message': 'Hi @user2'
    })
    m1 = messageResponse.json()
    
    requests.post(f"{url}message/react/v1", json={
        token: user2[token],
        'message_id': m1['message_id'],
        'react_id': thumbsUp
    })

    response = requests.get(f"{url}notifications/get/v1", params={
        "token": user1[token]
    })
    
    notifs = response.json()
    assert {
        cID: -1,
        dmID: dm1[dmID], 
        nMess: "user2 reacted to your message in user1, user2"
    } in notifs['notifications']
    assert len(notifs['notifications']) == 1
