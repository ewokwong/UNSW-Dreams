import pytest
import requests
import json
from src.config import url
from src.other import SECRET
from datetime import timezone, datetime
import jwt
import time

AuID     = 'auth_user_id'
uID      = 'u_id'
cID      = 'channel_id'
allMems  = 'all_members'
Name     = 'name'
dmName   = 'dm_name'
fName    = 'name_first'
lName    = 'name_last'
chans    = 'channels'
token    = 'token'
dmID     = 'dm_id'
handle   = 'handle_string'
ownMems  = 'owner_members'
mID      = 'message_id'
rID      = 'react_id'
thumbsUp = 1

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

#* Test if message_send is behaving according to spec
def test_http_message_send(user1, user2, user3, user4):
    c1 = requests.post(f"{url}channels/create/v2", json={
        "token": user1[token],
        "name": "TrumpPence",
        "is_public": True
    })
    requests.post(f"{url}channel/join/v2", json={
        "token": user2[token],
        "channel_id": c1.json()['channel_id']
    })
    requests.post(f"{url}channel/join/v2", json={
        "token": user3[token],
        "channel_id": c1.json()['channel_id']
    })
    message = ''
    for _ in range(1500):
        message += '?'
    assert requests.post(f"{url}message/send/v2", json={
        "token": user1[token],
        "channel_id": c1.json()['channel_id'],
        "message": message
    }).status_code == 400
    assert requests.post(f"{url}message/send/v2", json={
        "token": user4[token],
        "channel_id": c1.json()['channel_id'],
        "message": "?"
    }).status_code == 403
    m1 = requests.post(f"{url}message/send/v2", json={
        "token": user3[token],
        "channel_id": c1.json()['channel_id'],
        "message": "Sup"
    }).json()
    messageFound = False
    for messageDict in requests.get(f"{url}channel/messages/v2", params={
        "token": user1[token],
        "channel_id": c1.json()['channel_id'],
        "start": 0
    }).json()['messages']:
        if m1[mID] == messageDict[mID]:
            messageFound = True
            break
    assert messageFound is True

#* Test if message_edit is behaving according to spec
def test_http_message_edit(user1, user2, user3, user4):
    c1 = requests.post(f"{url}channels/create/v2", json={
        "token": user2[token],
        "name": "TrumpPence",
        "is_public": True
    })
    requests.post(f"{url}channel/join/v2", json={
        "token": user1[token],
        "channel_id": c1.json()['channel_id']
    })
    requests.post(f"{url}channel/join/v2", json={
        "token": user3[token],
        "channel_id": c1.json()['channel_id']
    })
    requests.post(f"{url}channel/join/v2", json={
        "token": user4[token],
        "channel_id": c1.json()['channel_id']
    })
    m1 = requests.post(f"{url}message/send/v2", json={
        "token": user3[token],
        "channel_id": c1.json()['channel_id'],
        "message": "Yo yo waz poppin'?"
    }).json()
    m2 = requests.post(f"{url}message/send/v2", json={
        "token": user3[token],
        "channel_id": c1.json()['channel_id'],
        "message": "Huh?"
    }).json()
    m3 = requests.post(f"{url}message/send/v2", json={
        "token": user3[token],
        "channel_id": c1.json()['channel_id'],
        "message": "John Cena"
    }).json()
    m4 = requests.post(f"{url}message/send/v2", json={
        "token": user3[token],
        "channel_id": c1.json()['channel_id'],
        "message": "Ricegum"
    }).json()
    requests.put(f"{url}message/edit/v2", json={
        "token": user1[token],
        "message_id": m1[mID],
        "message": "Jeffrey Meng"
    })
    editedMessage = {}
    for messageDict in requests.get(f"{url}channel/messages/v2", params={
        "token": user1[token],
        "channel_id": c1.json()['channel_id'],
        "start": 0
    }).json()['messages']:
        if m1[mID] == messageDict[mID]:
            editedMessage = messageDict
            break
    assert editedMessage['message'] == 'Jeffrey Meng'
    requests.put(f"{url}message/edit/v2", json={
        "token": user2[token],
        "message_id": m2[mID],
        "message": "Jeffrey Meng"
    })
    editedMessage = {}
    for messageDict in requests.get(f"{url}channel/messages/v2", params={
        "token": user2[token],
        "channel_id": c1.json()['channel_id'],
        "start": 0
    }).json()['messages']:
        if m2[mID] == messageDict[mID]:
            editedMessage = messageDict
            break
    assert editedMessage['message'] == 'Jeffrey Meng'
    requests.put(f"{url}message/edit/v2", json={
        "token": user3[token],
        "message_id": m3[mID],
        "message": "Jeffrey Meng"
    })
    editedMessage = {}
    for messageDict in requests.get(f"{url}channel/messages/v2", params={
        "token": user3[token],
        "channel_id": c1.json()['channel_id'],
        "start": 0
    }).json()['messages']:
        if m3[mID] == messageDict[mID]:
            editedMessage = messageDict
            break
    assert editedMessage['message'] == 'Jeffrey Meng'
    requests.put(f"{url}message/edit/v2", json={
        "token": user4[token],
        "message_id": m4[mID],
        "message": "Jeffrey Meng"
    }).status_code == 403
    requests.put(f"{url}message/edit/v2", json={
        "token": user3[token],
        "message_id": m3[mID],
        "message": ""
    })
    messageFound = False
    for messageDict in requests.get(f"{url}channel/messages/v2", params={
        "token": user3[token],
        "channel_id": c1.json()['channel_id'],
        "start": 0
    }).json()['messages']:
        if m3[mID] == messageDict[mID]:
            messageFound = True
            break
    assert messageFound is False
    requests.put(f"{url}message/edit/v2", json={
        "token": user2[token],
        "message_id": -1,
        "message": "Troll"
    }).status_code == 400
    tooLong = ""
    for _ in range(1001):
        tooLong += "?"
    requests.put(f"{url}message/edit/v2", json={
        "token": user2[token],
        "message_id": m4[mID],
        "message": tooLong
    }).status_code == 400
    d1 = requests.post(f"{url}dm/create/v1", json={
        "token": user1[token],
        "u_ids": [user2[AuID]]
    }).json()
    dM1 = requests.post(f"{url}message/senddm/v1", json={
        "token": user1[token],
        "dm_id": d1[dmID],
        "message": "Herp derp"
    }).json()
    requests.put(f"{url}message/edit/v2", json={
        "token": user2[token],
        "message_id": dM1[mID],
        "message": "Jeffrey Meng"
    }).status_code == 403

#* Test if message_remove is behaving according to spec
def test_http_message_remove(user1, user2, user3, user4):
    c1 = requests.post(f"{url}channels/create/v2", json={
        "token": user2[token],
        "name": "TrumpPence",
        "is_public": True
    })
    requests.post(f"{url}channel/join/v2", json={
        "token": user1[token],
        "channel_id": c1.json()['channel_id']
    })
    requests.post(f"{url}channel/join/v2", json={
        "token": user3[token],
        "channel_id": c1.json()['channel_id']
    })
    requests.post(f"{url}channel/join/v2", json={
        "token": user4[token],
        "channel_id": c1.json()['channel_id']
    })
    m1 = requests.post(f"{url}message/send/v2", json={
        "token": user3[token],
        "channel_id": c1.json()['channel_id'],
        "message": "Yo yo waz poppin'?"
    }).json()
    m2 = requests.post(f"{url}message/send/v2", json={
        "token": user3[token],
        "channel_id": c1.json()['channel_id'],
        "message": "Huh?"
    }).json()
    m3 = requests.post(f"{url}message/send/v2", json={
        "token": user3[token],
        "channel_id": c1.json()['channel_id'],
        "message": "John Cena"
    }).json()
    m4 = requests.post(f"{url}message/send/v2", json={
        "token": user3[token],
        "channel_id": c1.json()['channel_id'],
        "message": "Ricegum"
    }).json()
    requests.delete(f"{url}message/remove/v1", json={
        "token": user1[token],
        "message_id": m1[mID]
    })
    messageFound = False
    for messageDict in requests.get(f"{url}channel/messages/v2", params={
        "token": user1[token],
        "channel_id": c1.json()['channel_id'],
        "start": 0
    }).json()['messages']:
        if m1[mID] == messageDict[mID]:
            messageFound = True
            break
    assert messageFound is False
    requests.delete(f"{url}message/remove/v1", json={
        "token": user2[token],
        "message_id": m2[mID]
    })
    messageFound = False
    for messageDict in requests.get(f"{url}channel/messages/v2", params={
        "token": user2[token],
        "channel_id": c1.json()['channel_id'],
        "start": 0
    }).json()['messages']:
        if m2[mID] == messageDict[mID]:
            messageFound = True
            break
    assert messageFound is False
    requests.delete(f"{url}message/remove/v1", json={
        "token": user3[token],
        "message_id": m3[mID]
    })
    messageFound = False
    for messageDict in requests.get(f"{url}channel/messages/v2", params={
        "token": user3[token],
        "channel_id": c1.json()['channel_id'],
        "start": 0
    }).json()['messages']:
        if m3[mID] == messageDict[mID]:
            messageFound = True
            break
    assert messageFound is False
    assert requests.delete(f"{url}message/remove/v1", json={
        "token": user4[token],
        "message_id": m4[mID]
    }).status_code == 403
    assert requests.delete(f"{url}message/remove/v1", json={
        "token": user4[token],
        "message_id": -1
    }).status_code == 400

def test_http_message_share_todm(user1, user2, user3, user4):

    #* Test 1: create a channel and dm and share a channel message to the dm
    responseChannel = requests.post(f"{url}channels/create/v2", json={
        "token": user1[token],
        "name": 'Channel',
        "is_public": True}
    )
    channel = responseChannel.json()
    requests.post(f"{url}channel/invite/v2", json={
        "token": user1[token],
        "channel_id": channel[cID],
        "u_id": user2[AuID]}
    )
    dmresponse = requests.post(f"{url}dm/create/v1", json={
        "token": user2[token],
        "u_ids": [user3[AuID],user4[AuID]]}
    )
    dm = dmresponse.json()
    ogmsg = requests.post(f"{url}message/send/v2", json={
        "token": user1[token],
        "channel_id": channel['channel_id'],
        "message": 'hi'}
    )
    ogMessage = ogmsg.json()
    user2[token], ogMessage[mID],'', -1, dm[dmID]
    response = requests.post(f"{url}message/share/v1", json={
        "token": user2[token],
        "og_message_id": ogMessage[mID],
        "message": '',
        "channel_id": -1,
        dmID: dm[dmID] 
        })
    shared = response.json()

    check = requests.get(f"{url}dm/messages/v1", params={
        "token": user2[token],
        dmID: dm[dmID],
        'start' : 0,}
    )

    # verify message has been sent
    checklog = check.json()
    messageFound = False
    for messageDict in checklog['messages']:
        if shared["shared_message_id"] == messageDict[mID]:
            messageFound = True
            break
    assert messageFound is True 

    #* Test 2: if user1 is not in dmTest, raise access error
    
    response5 = requests.post(f"{url}message/share/v1", json={
        "token":user1[token],
        "og_message_id": ogMessage[mID],
        "message": '',
        "channel_id": -1,
        dmID: dm[dmID] 
        })
    assert response5.status_code == 403

#* When sending a message in a dm the user is not in, an AccessError is raised (403 response code)
def test_http_senddm_access_error(user1, user2, user3):
    dmResponse = requests.post(f"{url}dm/create/v1", json={
        "token": user1[token],
        "u_ids": [user2[AuID]]
    })
    dm1 = dmResponse.json()
    response = requests.post(f"{url}message/senddm/v1", json={
        token: user3[token],
        dmID: dm1[dmID],
        'message': ''
    })

    assert response.status_code == 403

#* When sending a message that is more than 1000 characters, an InputError is raised (400 response code)
def test_http_senddm_long(user1, user2):
    dmResponse = requests.post(f"{url}dm/create/v1", json={
        "token": user1[token],
        "u_ids": [user2[AuID]]
    })
    dm1 = dmResponse.json()
    message = 'a'*1001
    response = requests.post(f"{url}message/senddm/v1", json={
        token: user1[token],
        dmID: dm1[dmID],
        'message': message
    })

    assert response.status_code == 400

#* Asserts that when sending multiple dm messages, the message_id is increasing as expected
def test_http_senddm_multiple(user1, user2):
    dmResponse = requests.post(f"{url}dm/create/v1", json={
        "token": user1[token],
        "u_ids": [user2[AuID]]
    })
    dm1 = dmResponse.json()

    response0 = requests.post(f"{url}message/senddm/v1", json={
        token: user1[token],
        dmID: dm1[dmID],
        'message': ''
    })
    message0 = response0.json()
    assert message0 == {'message_id': message0['message_id']}
    response1 = requests.post(f"{url}message/senddm/v1", json={
        token: user1[token],
        dmID: dm1[dmID],
        'message': ''
    })

    message1 = response1.json()
    assert message1 == {'message_id': message1['message_id']}

    response2 = requests.post(f"{url}message/senddm/v1", json={
        token: user1[token],
        dmID: dm1[dmID],
        'message': ''
    })

    message2 = response2.json()
    assert message2 == {'message_id': message2['message_id']}
    
    response3 = requests.post(f"{url}message/senddm/v1", json={
        token: user1[token],
        dmID: dm1[dmID],
        'message': ''
    })

    message3 = response3.json()
    assert message3 == {'message_id': message3['message_id']}

#* Testing that a valid message is pinned for channel
def test_http_message_pin_valid_channel(user1):
    cResponse = requests.post(f"{url}channels/create/v2", json={
        "token": user1[token],
        "name": "Midsummer Madness",
        "is_public": True
    })
    channel = cResponse.json()

    requests.post(f"{url}message/send/v2", json={
        "token": user1[token],
        "channel_id": channel[cID],
        "message": 'Thumb it to summit'
    })

    mResponse = requests.post(f"{url}message/send/v2", json={
        "token": user1[token],
        "channel_id": channel[cID],
        "message": 'Pin it to win it'
    })
    target = mResponse.json()

    npResponse = requests.get(f"{url}channel/messages/v2", params={
        "token": user1[token],
        "channel_id": channel[cID],
        "start": 0
    })
    not_pinned = npResponse.json()
    
    mID_found = False
    for message in not_pinned['messages']:
        if target[mID] == message[mID]:
            mID_found = True
        assert message['is_pinned'] is False
    assert mID_found is True
    
    requests.post(f"{url}message/pin/v1", json={
        "token": user1[token],
        mID: target[mID]
    })
    
    pResponse = requests.get(f"{url}channel/messages/v2", params={
        "token": user1[token],
        "channel_id": channel[cID],
        "start": 0
    })
    pinned = pResponse.json()

    mID_found = False
    for message in pinned['messages']:
        if target[mID] == message[mID]:
            mID_found = True
            print(message)
            assert message['is_pinned'] is True
        else:
            assert message['is_pinned'] is False
    assert mID_found is True

#* Testing that a valid message is pinned for DM
def test_http_message_pin_valid_dm(user1, user2):
    dmResponse = requests.post(f"{url}dm/create/v1", json={
        "token": user1[token],
        "u_ids": [user2[AuID]]
    })
    dm = dmResponse.json()

    requests.post(f"{url}message/senddm/v1", json={
        token: user1[token],
        dmID: dm[dmID],
        'message': 'Thumb it to summit'
    })

    mResponse = requests.post(f"{url}message/senddm/v1", json={
        token: user1[token],
        dmID: dm[dmID],
        'message': 'Pin it to win it'
    })
    target = mResponse.json()

    npResponse = requests.get(f"{url}dm/messages/v1", params={
        token: user2[token],
        dmID: dm[dmID],
        'start' : 0,
    })
    not_pinned = npResponse.json()

    mID_found = False
    for message in not_pinned['messages']:
        if target[mID] == message[mID]:
            mID_found = True
        assert message['is_pinned'] is False
    assert mID_found is True

    requests.post(f"{url}message/pin/v1", json={
        token: user1[token],
        mID: target[mID]
    })
    
    pResponse = requests.get(f"{url}dm/messages/v1", params={
        token: user1[token],
        dmID: dm[dmID],
        "start": 0
    })
    pinned = pResponse.json()

    mID_found = False
    for message in pinned['messages']:
        if target[mID] == message[mID]:
            mID_found = True
            print(message)
            assert message['is_pinned'] is True
        else:
            assert message['is_pinned'] is False
    assert mID_found is True

#* Test that an InputError is raised when the message_id is invalid (error code 400)
def test_http_message_pin_invalid_mID(user1):
    invalid_mID = -1
    pResponse = requests.post(f"{url}message/pin/v1", json={
        token: user1[token],
        mID: invalid_mID
    })
    assert pResponse.status_code == 400

#* Test that an InputError is raised when trying to pin a pinned message (error code 400)
def test_http_message_pin_pinned(user1, user2):
    cResponse = requests.post(f"{url}channels/create/v2", json={
        "token": user1[token],
        "name": "CJWY",
        "is_public": True
    })
    channel = cResponse.json()

    m1Response = requests.post(f"{url}message/send/v2", json={
        "token": user1[token],
        "channel_id": channel[cID],
        "message": 'We got a number one victory royale'
    })
    m1 = m1Response.json()

    requests.post(f"{url}message/pin/v1", json={
        token: user1[token],
        mID: m1[mID]
    })

    e1Response = requests.post(f"{url}message/pin/v1", json={
        token: user1[token],
        mID: m1[mID]
    })
    assert e1Response.status_code == 400

    dmResponse = requests.post(f"{url}dm/create/v1", json={
        "token": user1[token],
        "u_ids": [user2[AuID]]
    })
    dm = dmResponse.json()

    m2Response = requests.post(f"{url}message/senddm/v1", json={
        token: user1[token],
        dmID: dm[dmID],
        'message': 'Yeah, Fortnite, we bout to get down'
    })
    m2 = m2Response.json()

    requests.post(f"{url}message/pin/v1", json={
        token: user1[token],
        mID: m2[mID]
    })

    e2Response = requests.post(f"{url}message/pin/v1", json={
        token: user1[token],
        mID: m2[mID]
    })
    assert e2Response.status_code == 400

#* Test that an AccessError is raised when trying to pin a message inside a channel/DM that they are not in (error code 403)
def test_http_message_pin_not_member(user1, user2, user3):
    cResponse = requests.post(f"{url}channels/create/v2", json={
        "token": user1[token],
        "name": 'Still CJWY',
        "is_public": True
    })
    channel = cResponse.json()
    
    m1Response = requests.post(f"{url}message/send/v2", json={
        "token": user1[token],
        "channel_id": channel[cID],
        "message": 'Ten kills on the board right now'
    })
    m1 = m1Response.json()

    e1Response = requests.post(f"{url}message/pin/v1", json={
        token: user3[token],
        mID: m1[mID]
    })
    assert e1Response.status_code == 403

    dmResponse = requests.post(f"{url}dm/create/v1", json={
        "token": user1[token],
        "u_ids": [user2[AuID]]
    })
    dm = dmResponse.json()

    m2Response = requests.post(f"{url}message/senddm/v1", json={
        token: user1[token],
        dmID: dm[dmID],
        'message': 'Pin it to win it'
    })
    m2 = m2Response.json()

    e2Response = requests.post(f"{url}message/pin/v1", json={
        token: user3[token],
        mID: m2[mID]
    })
    assert e2Response.status_code == 403

#* Testing that a valid message is unpinned for channel
def test_http_message_unpin_valid_channel(user1):
    cResponse = requests.post(f"{url}channels/create/v2", json={
        "token": user1[token],
        "name": 'Scissor Salad',
        "is_public": True
    })
    channel = cResponse.json()

    requests.post(f"{url}message/send/v2", json={
        "token": user1[token],
        "channel_id": channel[cID],
        "message": 'Le from downtown'
    })

    mResponse = requests.post(f"{url}message/send/v2", json={
        "token": user1[token],
        "channel_id": channel[cID],
        "message": 'AIRBALL'
    })
    target = mResponse.json()

    requests.post(f"{url}message/pin/v1", json={
        "token": user1[token],
        mID: target[mID]
    })

    pResponse = requests.get(f"{url}channel/messages/v2", params={
        "token": user1[token],
        "channel_id": channel[cID],
        "start": 0
    })
    pinned = pResponse.json()

    mID_found = False
    for message in pinned['messages']:
        if target[mID] == message[mID]:
            mID_found = True
            print(message)
            assert message['is_pinned'] is True
        else:
            assert message['is_pinned'] is False
    assert mID_found is True
    
    requests.post(f"{url}message/unpin/v1", json={
        "token": user1[token],
        mID: target[mID]
    })

    npResponse = requests.get(f"{url}channel/messages/v2", params={
        "token": user1[token],
        "channel_id": channel[cID],
        "start": 0
    })
    not_pinned = npResponse.json()

    mID_found = False
    for message in not_pinned['messages']:
        if target[mID] == message[mID]:
            mID_found = True
        assert message['is_pinned'] is False
    assert mID_found is True

#* Testing that a valid message is unpinned for DM
def test_http_message_unpin_valid_dm(user1, user2):
    dmResponse = requests.post(f"{url}dm/create/v1", json={
        "token": user1[token],
        "u_ids": [user2[AuID]]
    })
    dm = dmResponse.json()

    requests.post(f"{url}message/senddm/v1", json={
        token: user1[token],
        dmID: dm[dmID],
        'message': 'Thumb it to summit'
    })

    mResponse = requests.post(f"{url}message/senddm/v1", json={
        token: user1[token],
        dmID: dm[dmID],
        'message': 'Pin it to win it'
    })
    target = mResponse.json()

    requests.post(f"{url}message/pin/v1", json={
        token: user1[token],
        mID: target[mID]
    })

    pResponse = requests.get(f"{url}dm/messages/v1", params={
        token: user1[token],
        dmID: dm[dmID],
        "start": 0
    })
    pinned = pResponse.json()

    mID_found = False
    for message in pinned['messages']:
        if target[mID] == message[mID]:
            mID_found = True
            print(message)
            assert message['is_pinned'] is True
        else:
            assert message['is_pinned'] is False
    assert mID_found is True

    requests.post(f"{url}message/unpin/v1", json={
        token: user1[token],
        mID: target[mID]
    })

    npResponse = requests.get(f"{url}dm/messages/v1", params={
        token: user2[token],
        dmID: dm[dmID],
        'start' : 0,
    })
    not_pinned = npResponse.json()

    mID_found = False
    for message in not_pinned['messages']:
        if target[mID] == message[mID]:
            mID_found = True
        assert message['is_pinned'] is False
    assert mID_found is True

#* Test that an InputError is raised when the message_id is invalid (error code 400)
def test_http_test_message_unpin_invalid_mID(user1, user2):
    cResponse = requests.post(f"{url}channels/create/v2", json={
        "token": user1[token],
        "name": 'telepatia',
        "is_public": True
    })
    channel = cResponse.json()

    m1Response = requests.post(f"{url}message/send/v2", json={
        "token": user1[token],
        "channel_id": channel[cID],
        "message": 'Harry Houdini'
    })
    m1 = m1Response.json()

    requests.post(f"{url}message/pin/v1", json={
        token: user1[token],
        mID: m1[mID]
    })
    requests.delete(f"{url}message/remove/v1", json={
        "token": user1[token],
        "message_id": m1[mID]
    })

    e1Response = requests.post(f"{url}message/unpin/v1", json={
        token: user1[token],
        mID: m1[mID]
    })
    assert e1Response.status_code == 400

    dmResponse = requests.post(f"{url}dm/create/v1", json={
        "token": user1[token],
        "u_ids": [user2[AuID]]
    })
    dm = dmResponse.json()

    m2Response = requests.post(f"{url}message/senddm/v1", json={
        token: user1[token],
        dmID: dm[dmID],
        'message': 'He gone'
    })
    m2 = m2Response.json()

    requests.post(f"{url}message/pin/v1", json={
        token: user1[token],
        mID: m2[mID]
    })
    requests.delete(f"{url}message/remove/v1", json={
        "token": user1[token],
        "message_id": m2[mID]
    })

    e2Response = requests.post(f"{url}message/unpin/v1", json={
        token: user1[token],
        mID: m2[mID]
    })
    assert e2Response.status_code == 400

#* Test that an InputError is raised when trying to unpin an unpinned message (error code 400)
def test_http_message_unpin_unpinned_(user1, user2):
    cResponse = requests.post(f"{url}channels/create/v2", json={
        "token": user1[token],
        "name": 'Vincent Le',
        "is_public": True
    })
    channel = cResponse.json()

    m1Response = requests.post(f"{url}message/send/v2", json={
        "token": user1[token],
        "channel_id": channel[cID],
        "message": 'Noted'
    })
    m1 = m1Response.json()

    e1Response = requests.post(f"{url}message/unpin/v1", json={
        token: user1[token],
        mID: m1[mID]
    })
    assert e1Response.status_code == 400

    dmResponse = requests.post(f"{url}dm/create/v1", json={
        "token": user1[token],
        "u_ids": [user2[AuID]]
    })
    dm = dmResponse.json()

    m2Response = requests.post(f"{url}message/senddm/v1", json={
        token: user1[token],
        dmID: dm[dmID],
        'message': 'Noted'
    })
    m2 = m2Response.json()

    e2Response = requests.post(f"{url}message/unpin/v1", json={
        token: user1[token],
        mID: m2[mID]
    })
    assert e2Response.status_code == 400

#* Test that an AccessError is raised when trying to unpin a message inside a channel/DM that are not in (error code 403)
def test_http_message_unpin_not_member(user1, user2, user3):
    cResponse = requests.post(f"{url}channels/create/v2", json={
        "token": user1[token],
        "name": 'Should really',
        "is_public": True
    })
    channel = cResponse.json()

    m1Response = requests.post(f"{url}message/send/v2", json={
        "token": user1[token],
        "channel_id": channel[cID],
        "message": 'fixture these'
    })
    m1 = m1Response.json()

    requests.post(f"{url}message/pin/v1", json={
        token: user1[token],
        mID: m1[mID]
    })

    e1Response = requests.post(f"{url}message/unpin/v1", json={
        token: user2[token],
        mID: m1[mID]
    })
    assert e1Response.status_code == 403

    e2Response = requests.post(f"{url}message/unpin/v1", json={
        token: user3[token],
        mID: m1[mID]
    })
    assert e2Response.status_code == 403

    dmResponse = requests.post(f"{url}dm/create/v1", json={
        "token": user1[token],
        "u_ids": [user2[AuID]]
    })
    dm = dmResponse.json()

    m2Response = requests.post(f"{url}message/senddm/v1", json={
        token: user1[token],
        dmID: dm[dmID],
        'message': 'ASAP'
    })
    m2 = m2Response.json()

    requests.post(f"{url}message/pin/v1", json={
        token: user1[token],
        mID: m2[mID]
    })

    e3Response = requests.post(f"{url}message/unpin/v1", json={
        token: user3[token],
        mID: m1[mID]
    })
    assert e3Response.status_code == 403

#* Testing that for an invalid token, an AccessError is raised for 'pin' functions (error code 403)
def test_http_message_pin_unauthorised_user(user1, invalid_token):
    cResponse = requests.post(f"{url}channels/create/v2", json={
        "token": user1[token],
        "name": 'Iteration 3',
        "is_public": True
    })
    channel = cResponse.json()

    m1Response = requests.post(f"{url}message/send/v2", json={
        "token": user1[token],
        "channel_id": channel[cID],
        "message": 'Last one'
    })
    m1 = m1Response.json()

    m2Response = requests.post(f"{url}message/send/v2", json={
        "token": user1[token],
        "channel_id": channel[cID],
        "message": 'and we outta here'
    })
    m2 = m2Response.json()

    requests.post(f"{url}message/pin/v1", json={
        token: user1[token],
        mID: m2[mID]
    })

    e1Response = requests.post(f"{url}message/pin/v1", json={
        token: invalid_token,
        mID: m1[mID]
    })
    assert e1Response.status_code == 403

    e1Response = requests.post(f"{url}message/unpin/v1", json={
        token: invalid_token,
        mID: m2[mID]
    })
    assert e1Response.status_code == 403
    
#Message_react
#Input Error test for invalid message id for message_react
def test_http_message_react_v1_errors_invalid_mID(user1):
    invalid_mID = -1
    result = requests.post(f"{url}message/react/v1", json= {
        token: user1[token],
        mID: invalid_mID,
        rID: thumbsUp,
    })
    
    assert result.status_code == 400

#Input error test for invalid react id for message_react 
def test_http_message_react_v1_errors_invalid_rID(user1, user2):
    invalid_rID = -1
    
    #Invalid rID for channel 
    channel = requests.post(f"{url}channels/create/v2", json={
        "token": user1[token],
        "name": 'Iteration 3',
        "is_public": True
    }).json()
    
    result = requests.post(f"{url}message/send/v2", json={
        "token": user1[token],
        "channel_id": channel[cID],
        "message": 'First one'
    })
    
    m1 = result.json()
    response = requests.post(f"{url}message/react/v1", json= {
        token: user1[token],
        mID: m1[mID],
        rID: invalid_rID,
    })
    assert response.status_code == 400
    
    #Invalid rID for DM
    result2 = requests.post(f"{url}dm/create/v1", json={
        token: user1[token],
        "u_ids": [user2[AuID]]
    })
    dm1 = result2.json()
    
    result3 = requests.post(f"{url}message/senddm/v1", json={
        token: user1[token],
        dmID: dm1[dmID],
        'message': 'Second one'
    })
    
    m2 = result3.json()
    
    response2 = requests.post(f"{url}message/react/v1", json= {
        token: user1[token],
        mID: m2[mID],
        rID: invalid_rID,
    })
    assert response2.status_code == 400

#Test that already contains an active react raises input error
def test_http_message_react_v1_active_react(user1, user2):
    #Already contains react in channel 
    channel = requests.post(f"{url}channels/create/v2", json={
        "token": user1[token],
        "name": 'Iteration 3',
        "is_public": True
    }).json()
    result = requests.post(f"{url}message/send/v2", json={
        "token": user1[token],
        "channel_id": channel[cID],
        "message": 'First one'
    })
    m1 = result.json()
    
    requests.post(f"{url}message/react/v1", json= {
        token: user1[token],
        mID: m1[mID],
        rID: thumbsUp,
    })
    
    #Second react with already active react 
    response = requests.post(f"{url}message/react/v1", json= {
        token: user1[token],
        mID: m1[mID],
        rID: thumbsUp,
    })
    assert response.status_code == 400
    
    #Already contains react in DM 
    dm = requests.post(f"{url}dm/create/v1", json={
        token: user1[token],
        "u_ids": [user2[AuID]]
    }).json()
    result2 = requests.post(f"{url}message/senddm/v1", json={
        token: user1[token],
        dmID: dm[dmID],
        'message': 'Second one'
    })
    m2 = result2.json()
    
    requests.post(f"{url}message/react/v1", json= {
        token: user1[token],
        mID: m2[mID],
        rID: thumbsUp,
    })
    
    #Second react with already active react 
    response2 = requests.post(f"{url}message/react/v1", json= {
        token: user1[token],
        mID: m2[mID],
        rID: thumbsUp,
    })
    assert response2.status_code == 400
   
#Test that authorised user not a member of channel or dm raises access error for message_react 
def test_http_message_react_v1_invalid_user(user1, user2, user3): 
    #Not a member of channel 
    channel = requests.post(f"{url}channels/create/v2", json={
        "token": user1[token],
        "name": 'Iteration 3',
        "is_public": False
    }).json()
    
    result = requests.post(f"{url}message/send/v2", json={
        "token": user1[token],
        "channel_id": channel[cID],
        "message": 'First one'
    })
    m1 = result.json()
    
    response = requests.post(f"{url}message/react/v1", json= {
        token: user2[token],
        mID: m1[mID],
        rID: thumbsUp,
    })
    assert response.status_code == 403
    
    #Not a member of DM
    dm = requests.post(f"{url}dm/create/v1", json={
        token: user1[token],
        "u_ids": [user2[AuID]]
    }).json()
    
    result2 = requests.post(f"{url}message/senddm/v1", json={
        token: user1[token],
        dmID: dm[dmID],
        'message': 'Second one'
    })
    m2 = result2.json()
    
    response2 = requests.post(f"{url}message/react/v1", json= {
        token: user3[token],
        mID: m2[mID],
        rID: thumbsUp,
    })
    
    assert response2.status_code == 403

#Test that message_react works for a message in a channel
def test_http_message_react_v1_valid_channel(user1, user2):
    channel = requests.post(f"{url}channels/create/v2", json={
        "token": user1[token],
        "name": 'Iteration 3',
        "is_public": True
    }).json()
    
    result = requests.post(f"{url}message/send/v2", json={
        "token": user1[token],
        "channel_id": channel[cID],
        "message": 'First one'
    })
    m1 = result.json()
    
    requests.post(f"{url}message/react/v1", json= {
        token: user1[token],
        mID: m1[mID],
        rID: thumbsUp,
    })

    #Find the message and look in its reacts['u_ids'] to find user_1[AuID]
    check = requests.get(f"{url}channel/messages/v2", params={
        token: user1[token],
        cID: channel[cID] ,
        'start' : 0,}
    )

    #Instead of this, can assert that is_this_user reacted is true for message with same message id and react ID
    checklog = check.json()
    
    for current_message in checklog['messages']: 
        if current_message[mID] == m1[mID]: 
            #Now that the message is found, can assert that our user has reacted to it    
            for current_react in current_message['reacts']: 
                if current_react['react_id'] == thumbsUp:
                    assert user1[AuID] in current_react['u_ids'] 
                assert current_react['is_this_user_reacted'] == True 

#Test that message_react works for a dm 
def test_http_message_react_v1_valid_dm(user1, user2):
    dm = requests.post(f"{url}dm/create/v1", json={
        token: user1[token],
        "u_ids": [user2[AuID]]
    }).json()
    
    result = requests.post(f"{url}message/senddm/v1", json={
        token: user1[token],
        dmID: dm[dmID],
        'message': 'First one'
    })
    m1 = result.json()
    
    requests.post(f"{url}message/react/v1", json= {
        token: user1[token],
        mID: m1[mID],
        rID: thumbsUp,
    })
    
    #Assert that is_this_user reacted is true when dm_messages is called for that message with message_id and same rID
    check = requests.get(f"{url}dm/messages/v1", params={
        token: user1[token],
        dmID: dm[dmID] ,
        'start' : 0,}
    )
    
    checklog = check.json()
    for current_message in checklog['messages']: 
        if current_message[mID] == m1[mID]: 
            #Now that the message is found, can assert that our user has reacted to it       
            for current_react in current_message['reacts']: 
                if current_react['react_id'] == thumbsUp:
                    assert user1[AuID] in current_react['u_ids'] 
                assert current_react['is_this_user_reacted'] == True 
                    
#Message_unreact
#Input Error test for invalid message id for message_unreact
def test_http_message_unreact_v1_errors_invalid_mID(user1, user2):
    invalid_mID = -1
    result = requests.post(f"{url}message/unreact/v1", json= {
        token: user1[token],
        mID: invalid_mID,
        rID: thumbsUp,
    })
    assert result.status_code == 400

#Input error test for invalid react id for message_unreact 
def test_http_message_unreact_v1_errors_invalid_rID(user1, user2): 
    invalid_rID = -1
    
    #Invalid rID for channel 
    channel = requests.post(f"{url}channels/create/v2", json={
        "token": user1[token],
        "name": 'Iteration 3',
        "is_public": True
    }).json()
    
    result = requests.post(f"{url}message/send/v2", json={
        "token": user1[token],
        "channel_id": channel[cID],
        "message": 'First one'
    })
    
    m1 = result.json()
    response = requests.post(f"{url}message/unreact/v1", json= {
        token: user1[token],
        mID: m1[mID],
        rID: invalid_rID,
    })
    assert response.status_code == 400
    
    #Invalid rID for DM
    result2 = requests.post(f"{url}dm/create/v1", json={
        token: user1[token],
        "u_ids": [user2[AuID]]
    })
    dm = result2.json()
    
    result3 = requests.post(f"{url}message/senddm/v1", json={
        token: user1[token],
        dmID: dm[dmID],
        'message': 'Second one'
    })
    
    m2 = result3.json()
    
    response2 = requests.post(f"{url}message/unreact/v1", json= {
        token: user1[token],
        mID: m2[mID],
        rID: invalid_rID,
    })
    assert response2.status_code == 400

#Test that doesn't contain react raises input error for message_unreact
def test_http_message_unreact_v1_active_react(user1, user2):
    #Doesn't contain react in channel 
    channel = requests.post(f"{url}channels/create/v2", json={
        "token": user1[token],
        "name": 'Iteration 3',
        "is_public": True
    }).json()
    result = requests.post(f"{url}message/send/v2", json={
        "token": user1[token],
        "channel_id": channel[cID],
        "message": 'First one'
    })
    m1 = result.json()
        
    #React with no active react  
    response = requests.post(f"{url}message/unreact/v1", json= {
        token: user1[token],
        mID: m1[mID],
        rID: thumbsUp,
    })
    assert response.status_code == 400
    
    #No react in DM 
    dm = requests.post(f"{url}dm/create/v1", json={
        token: user1[token],
        "u_ids": [user2[AuID]]
    }).json()
    result2 = requests.post(f"{url}message/senddm/v1", json={
        token: user1[token],
        dmID: dm[dmID],
        'message': 'Second one'
    })
    m2 = result2.json()

    response2 = requests.post(f"{url}message/unreact/v1", json= {
        token: user1[token],
        mID: m2[mID],
        rID: thumbsUp,
    })
    assert response2.status_code == 400

#Test that authorised user not a member of channel or dm raises access error for message_unreact 
def test_http_message_unreact_v1_invalid_user(user1, user2, user3): 
    #Not a member of channel 
    channel = requests.post(f"{url}channels/create/v2", json={
        "token": user1[token],
        "name": 'Iteration 3',
        "is_public": False
    }).json()
    
    result = requests.post(f"{url}message/send/v2", json={
        "token": user1[token],
        "channel_id": channel[cID],
        "message": 'First one'
    })
    m1 = result.json()
    
    response = requests.post(f"{url}message/unreact/v1", json= {
        token: user2[token],
        mID: m1[mID],
        rID: thumbsUp,
    })
    assert response.status_code == 403
    
    #Not a member of DM
    dm = requests.post(f"{url}dm/create/v1", json={
        token: user1[token],
        "u_ids": [user2[AuID]]
    }).json()
    
    result2 = requests.post(f"{url}message/senddm/v1", json={
        token: user1[token],
        dmID: dm[dmID],
        'message': 'Second one'
    })
    m2 = result2.json()
    
    response2 = requests.post(f"{url}message/unreact/v1", json= {
        token: user3[token],
        mID: m2[mID],
        rID: thumbsUp,
    })
    assert response2.status_code == 403

#Test that message_unreact works for a message in a channel
def test_http_message_unreact_v1_valid_channel(user1, user2):
    channel = requests.post(f"{url}channels/create/v2", json={
        "token": user1[token],
        "name": 'Iteration 3',
        "is_public": True
    }).json()
    
    result = requests.post(f"{url}message/send/v2", json={
        "token": user1[token],
        "channel_id": channel[cID],
        "message": 'First one'
    })
    m1 = result.json()
    
    requests.post(f"{url}message/react/v1", json= {
        token: user1[token],
        mID: m1[mID],
        rID: thumbsUp,
    })
    
    requests.post(f"{url}message/unreact/v1", json= {
        token: user1[token],
        mID: m1[mID],
        rID: thumbsUp,
    })
    
    check = requests.get(f"{url}channel/messages/v2", params={
        token: user1[token],
        cID: channel[cID] ,
        'start' : 0,}
    )
    
    message_log = check.json()
    #Go through check and find that is this user for messages is False 
    for current_message in message_log['messages']: 
        if current_message[mID] == m1[mID]: 
            #Now that the message is found, can assert that our user has reacted to it  
            for current_react in current_message['reacts']: 
                if current_react['react_id'] == thumbsUp:
                    assert user1[AuID] not in current_react['u_ids']
                assert current_react['is_this_user_reacted'] == False 
    
#Test that message_unreact works for a dm 
def test_http_message_unreact_v1_valid_dm(user1, user2):
    dm = requests.post(f"{url}dm/create/v1", json={
        token: user1[token],
        "u_ids": [user2[AuID]]
    }).json()
    
    result = requests.post(f"{url}message/senddm/v1", json={
        token: user1[token],
        dmID: dm[dmID],
        'message': 'First one'
    })
    m1 = result.json()
    
    requests.post(f"{url}message/react/v1", json= {
        token: user1[token],
        mID: m1[mID],
        rID: thumbsUp,
    })
    requests.post(f"{url}message/unreact/v1", json= {
        token: user1[token],
        mID: m1[mID],
        rID: thumbsUp,
    })
    
    #Assert that is_this_user reacted is true when dm_messages is called for that message with message_id and same rID
    check = requests.get(f"{url}dm/messages/v1", params={
        token: user1[token],
        dmID: dm[dmID] ,
        'start' : 0,}
    )
    
    message_log = check.json()
    for current_message in message_log['messages']: 
        if current_message[mID] == m1[mID]: 
            #Now that the message is found, can assert that our user has reacted to it       
            for current_react in current_message['reacts']: 
                if current_react['react_id'] == thumbsUp:
                    assert user1[AuID] not in current_react['u_ids'] 
                assert current_react['is_this_user_reacted'] == False
    


#* Testing a message that is to be sent later isn't prematurely sent
#* And is actually sent in the end with correct timestamp
def test_http_message_sendlater(user1, user2):
    c1 = requests.post(f"{url}channels/create/v2", json={
        "token": user1[token],
        "name": "TrumpPence",
        "is_public": True
    })
    requests.post(f"{url}channel/join/v2", json={
        "token": user2[token],
        "channel_id": c1.json()['channel_id']
    })
    sendTime = datetime.now().replace(tzinfo=timezone.utc).timestamp() + 3
    m1 = requests.post(f"{url}message/sendlater/v1", json={
        "token": user1[token],
        "channel_id": c1.json()['channel_id'],
        "message": "You know what matters more than American Muscle?",
        "time_sent": sendTime
    })
    messageFound = False
    for message in requests.get(f"{url}channel/messages/v2", params={
        "token": user2[token],
        "channel_id": c1.json()[cID],
        "start": 0
    }).json()['messages']:
        if m1.json()['message_id'] == message['message_id']:
            messageFound = True
    assert not messageFound

    #* Sleep for now
    time.sleep(4)

    for message in requests.get(f"{url}channel/messages/v2", params={
        "token": user2[token],
        "channel_id": c1.json()[cID],
        "start": 0
    }).json()['messages']:
        if m1.json()['message_id'] == message['message_id']:
            mTime = message['time_created']
            messageFound = True
    assert messageFound
    assert mTime == sendTime

#* Testing a message that is to be sent later isn't prematurely sent
#* And is actually sent in the end with correct timestamp
def test_http_message_sendlaterdm(user1, user2):
    d1 = requests.post(f"{url}dm/create/v1", json={
        "token": user1[token],
        "u_ids": [user2[AuID]]
    })
    sendTime = datetime.now().replace(tzinfo=timezone.utc).timestamp() + 3
    m1 = requests.post(f"{url}message/sendlaterdm/v1", json={
        "token": user1[token],
        "dm_id": d1.json()[dmID],
        "message": "You know what matters more than American Muscle?",
        "time_sent": sendTime
    })
    messageFound = False
    for message in requests.get(f"{url}dm/messages/v1", params={
        "token": user2[token],
        "dm_id": d1.json()[dmID],
        "start": 0
    }).json()['messages']:
        if m1.json()['message_id'] == message['message_id']:
            messageFound = True
    assert not messageFound

    #* Sleep for now
    time.sleep(4)

    for message in requests.get(f"{url}dm/messages/v1", params={
        "token": user2[token],
        "dm_id": d1.json()[dmID],
        "start": 0
    }).json()['messages']:
        if m1.json()['message_id'] == message['message_id']:
            mTime = message['time_created']
            messageFound = True
    assert messageFound
    assert mTime == sendTime
