import pytest
import requests
import json
from src.config import url
from src.other import SECRET
import jwt
from src.channels import channels_create_v1
from src.message import message_send_v1
from src.config import url

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
handle  = 'handle_str'
ownMems = 'owner_members'

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


def test_http_channel_invite(user1, user2, user3):
    
    responseChannel = requests.post(f"{url}channels/create/v2", json={
        "token": user1[token],
        "name": 'Channel1',
        "is_public": True}
    )
    #* Test 1: Invite user2 into channel1 should be successful
    channel1 = responseChannel.json()
    requests.post(f"{url}channel/invite/v2", json={
        "token": user1[token],
        "channel_id": channel1[cID],
        "u_id": user2[AuID]}
    )
    response = requests.get(f"{url}channel/details/v2", params={
        'token': user1[token],
        'channel_id': channel1[cID]}
    )
    details = response.json()
    assert {
        fName: 'User', 
        lName: '2', 
        'email': "second@gmail.com", 
        'handle_str': "user2",
        uID: user2[AuID],
        'profile_img_url': f"{url}static/default.jpg"
    } in details[allMems]

    #* Test 2: Channel id not valid raises inputerror
    response2 = requests.post(f"{url}channel/invite/v2", json={
        "token": user1[token],
        "channel_id": -1,
        "u_id": user2[AuID]}
    )

    assert response2.status_code == 400

    #* Test 3: user id not valid raises inputerror
    response3 = requests.post(f"{url}channel/invite/v2", json={
        "token": user1[token],
        "channel_id": user1[token],
        "u_id": -1}
    )

    assert response3.status_code == 400

    #* Test 4: user not in chnanel raises accesserror
    response4 = requests.post(f"{url}channel/invite/v2", json={
        "token": user3[token],
        "channel_id": channel1[cID],
        "u_id": user2[AuID]}
    )

    assert response4.status_code == 403

def test_http_channel_details(user1, user2):

    responseChannel = requests.post(f"{url}channels/create/v2", json={
        "token": user1[token],
        "name": 'Channel1',
        "is_public": True}
    )
    channel1 = responseChannel.json()

    #* Test 1: expected channel details
    expected = {'name': "Channel1",
        'is_public': True, 
        'owner_members':[{
            'u_id': user1[AuID],
            'name_first': "User",
            'name_last': '1',
            'email': 'first@gmail.com',
            'handle_str': 'user1',
            'profile_img_url': f"{url}static/default.jpg"
        }],
        'all_members':[{
            'u_id': user1[AuID], 
            'name_first': "User",
            'name_last': '1',
            'email': 'first@gmail.com',
            'handle_str': 'user1',
            'profile_img_url': f"{url}static/default.jpg"
        }]
    }

    responseUser = requests.get(f"{url}channel/details/v2", params = {'token': user1[token], 'channel_id': channel1[cID]})

    assert responseUser.json() == expected

    #* Test 2: InputERRor when, channel id not a valid id
    response1 = requests.get(f"{url}channel/details/v2", params = {'token': user1[token], 'channel_id': -1})

    assert response1.status_code == 400

    #* Test 3 : AccessError when user not in channel
    responseUser2 = requests.get(f"{url}channel/details/v2", params = {'token': user2[token], 'channel_id': channel1[cID]})

    assert responseUser2.status_code == 403


def test_http_channel_leave(user1, user2, user3, user4):
    #* Public channel is created by user1
    c1 = requests.post(f"{url}channels/create/v2", json={
        "token": user1[token],
        "name": "TrumpPence",
        "is_public": True
    })
    #* Users 2, 3 and 4 join this channel
    requests.post(f"{url}channel/join/v2", json={
        "token": user2[token],
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
    #* Make sure they joined
    assert {
        uID: user2[AuID],
        fName: 'User',
        lName: "2",
        'email': "second@gmail.com",
        'handle_str': "user2",
        'profile_img_url': f"{url}static/default.jpg"
    } in requests.get(f"{url}channel/details/v2", params={
        'token': user3[token], 
        'channel_id': c1.json()['channel_id']
    }).json()[allMems]
    assert {
        uID: user3[AuID],
        fName: 'User',
        lName: "3",
        'email': "third@gmail.com",
        'handle_str': "user3",
        'profile_img_url': f"{url}static/default.jpg"
    } in requests.get(f"{url}channel/details/v2", params={
        'token': user3[token], 
        'channel_id': c1.json()['channel_id']
    }).json()[allMems]
    assert {
        uID: user4[AuID],
        fName: 'User',
        lName: "4",
        'email': "fourth@gmail.com",
        'handle_str': "user4",
        'profile_img_url': f"{url}static/default.jpg"
    } in requests.get(f"{url}channel/details/v2", params={
        'token': user3[token], 
        'channel_id': c1.json()['channel_id']
    }).json()[allMems]
    #* User 4 leaves and make sure he left
    requests.post(f"{url}channel/leave/v1", json={
        "token": user4[token],
        "channel_id": c1.json()['channel_id']
    })
    assert {
        uID: user4[AuID],
        fName: 'User',
        lName: "4",
        'email': "fourth@gmail.com",
        'handle_str': "user4",
        'profile_img_url': f"{url}static/default.jpg"
    } not in requests.get(f"{url}channel/details/v2", params={
        'token': user1[token], 
        'channel_id': c1.json()['channel_id']
    }).json()[allMems]
    #* User 3 leaves and make sure he left
    requests.post(f"{url}channel/leave/v1", json={
        "token": user3[token],
        "channel_id": c1.json()['channel_id']
    })
    assert {
        uID: user3[AuID],
        fName: 'User',
        lName: "3",
        'email': "third@gmail.com",
        'handle_str': "user3",
        'profile_img_url': f"{url}static/default.jpg"
    } not in requests.get(f"{url}channel/details/v2", params={
        'token': user1[token], 
        'channel_id': c1.json()['channel_id']
    }).json()[allMems]

    #* Make sure User 3 cannot leave (already left)
    assert requests.post(f"{url}channel/leave/v1", json={
        "token": user3[token],
        "channel_id": c1.json()['channel_id']
    }).status_code == 403
    #* Make sure cannot leave a channel that doesn't exist
    assert requests.post(f"{url}channel/leave/v1", json={
        "token": user3[token],
        "channel_id": -1
    }).status_code == 400

def test_http_channel_join(user1, user2, user3, user4):
    #* This test is structured identically to test_channel_join in tests/channel_test.py
    c1 = requests.post(f"{url}channels/create/v2", json={
        "token": user1[token],
        "name": "TrumpPence",
        "is_public": True
    })
    c2 = requests.post(f"{url}channels/create/v2", json={
        "token": user2[token],
        "name": "BidenHarris",
        "is_public": False
    })
    requests.post(f"{url}channel/join/v2", json={
        "token": user3[token],
        "channel_id": c1.json()['channel_id']
    })
    assert requests.get(f"{url}channel/details/v2", params={
        'token': user3[token], 
        'channel_id': c1.json()['channel_id']
    }).json() == {
        "name": "TrumpPence",
        "is_public": True,
        "owner_members": [
            {
                uID: user1[AuID],
                'email': "first@gmail.com",
                fName: "User",
                lName: "1",
                'handle_str': "user1",
                'profile_img_url': f"{url}static/default.jpg"
            }
        ],
        "all_members": [
            {
                uID: user1[AuID],
                'email': "first@gmail.com",
                fName: "User",
                lName: "1",
                'handle_str': "user1",
                'profile_img_url': f"{url}static/default.jpg"
            },
            {
                uID: user3[AuID],
                'email': "third@gmail.com",
                fName: "User",
                lName: "3",
                'handle_str': "user3",
                'profile_img_url': f"{url}static/default.jpg"
            }
        ]
    }
    assert requests.post(f"{url}channel/join/v2", json={
        "token": user4[token],
        "channel_id": c2.json()['channel_id']
    }).status_code == 403
    assert requests.get(f"{url}channel/details/v2", params={
        "token": user3[token],
        "channel_id": c2.json()['channel_id']
    }).status_code == 403
    assert requests.get(f"{url}channel/details/v2", params={
        "token": user4[token],
        "channel_id": c1.json()['channel_id']
    }).status_code == 403
    assert requests.post(f"{url}channel/join/v2", json={
        "token": user4[token],
        "channel_id": -1
    }).status_code == 400

def test_http_channel_addowner(user1, user2, user3, user4):

    responseChannel = requests.post(f"{url}channels/create/v2", json={
        "token": user1[token],
        "name": 'Channel1',
        "is_public": True}
    )
    channel1 = responseChannel.json() 

    #* Test 1: Succesfully add owner

    requests.post(f"{url}channel/addowner/v1", json={
        "token": user1[token],
        "channel_id": channel1[cID],
        "u_id": user2[AuID]}
    )

    response = requests.get(f"{url}channel/details/v2", params={
        'token': user1[token],
        'channel_id': channel1[cID]}
    )
    details = response.json()

    assert {
        uID: user2[AuID],
        fName: 'User',
        lName: '2',
        'email': 'second@gmail.com',
        'handle_str': 'user2',
        'profile_img_url': f"{url}static/default.jpg"
    } in details[allMems]
    assert {
        uID: user2[AuID],
        fName: 'User',
        lName: '2',
        'email': 'second@gmail.com',
        'handle_str': 'user2',
        'profile_img_url': f"{url}static/default.jpg"
    } in details[ownMems]

    #* Test 2: Input error for invalid Channel iD

    response2 = requests.post(f"{url}channel/addowner/v1", json={
        "token": user1[token],
        "channel_id": -1,
        "u_id": user3[AuID]}
    )

    assert response2.status_code == 400

    #* Test 3: Input error when user is already an owner
    response3 = requests.post(f"{url}channel/addowner/v1", json={
        "token": user1[token],
        "channel_id": channel1[cID],
        "u_id": user2[AuID]}
    )

    assert response3.status_code == 400

    #* Test 4: Access error when user not owner or owner of channel

    response4 = requests.post(f"{url}channel/addowner/v1", json={
        "token": user3[token],
        "channel_id": channel1[cID],
        "u_id": user4[AuID]}
    )

    assert response4.status_code == 403

def test_http_channel_removeowner(user1, user2, user3, user4):
    
    responseChannel = requests.post(f"{url}channels/create/v2", json={
        "token": user1[token],
        "name": 'Channel1',
        "is_public": True}
    )
    channel1 = responseChannel.json() 
    #* Test 1 : see if successfully removed member from owner not all members
    requests.post(f"{url}channel/addowner/v1", json={
        "token": user1[token],
        "channel_id": channel1[cID],
        "u_id": user2[AuID]}
    )

    requests.post(f"{url}channel/removeowner/v1", json={
        "token": user2[token],
        "channel_id": channel1[cID],
        "u_id": user1[AuID]}
    )

    response = requests.get(f"{url}channel/details/v2", params={
        'token': user2[token],
        'channel_id': channel1[cID]}
    )
    details = response.json()

    assert {
        uID: user1[AuID],
        fName: 'User',
        lName: '1',
        'email': 'first@gmail.com',
        'handle_str': 'user1',
        'profile_img_url': f"{url}static/default.jpg"
    } not in details[ownMems]
    assert {
        uID: user1[AuID],
        fName: 'User',
        lName: '1',
        'email': 'first@gmail.com',
        'handle_str': 'user1',
        'profile_img_url': f"{url}static/default.jpg"
    } in details[allMems]

    #* Test 2: Input Error for channel ID not valid

    requests.post(f"{url}channel/addowner/v1", json={
        "token": user2[token],
        "channel_id": channel1[cID],
        "u_id": user1[AuID]}
    )
    response2 = requests.post(f"{url}channel/removeowner/v1", json={
        "token": user1[token],
        "channel_id": -1,
        "u_id": user2[AuID]}
    )

    assert response2.status_code == 400

    #* Test 3: Input error when user is not an owner
    response3 = requests.post(f"{url}channel/removeowner/v1", json={
        "token": user1[token],
        "channel_id": channel1[cID],
        "u_id": user3[AuID]}
    )

    assert response3.status_code == 400

    #* Test 4: Input error when user is only owner
    requests.post(f"{url}channel/removeowner/v1", json={
        "token": user2[token],
        "channel_id": channel1[cID],
        "u_id": user1[AuID]}
    )

    response4 = requests.post(f"{url}channel/removeowner/v1", json={
        "token": user2[token],
        "channel_id": channel1[cID],
        "u_id": user2[AuID]}
    )

    assert response4.status_code == 400

    #* Test 5: Access Error when user is not owner of dreams
    responseChannel2 = requests.post(f"{url}channels/create/v2", json={
        "token": user2[token],
        "name": 'Channel2',
        "is_public": True}
    )
    channel2 = responseChannel2.json() 
    requests.post(f"{url}channel/addowner/v1", json={
        "token": user2[token],
        "channel_id": channel2[cID],
        "u_id": user1[AuID]}
    )
    response5 = requests.post(f"{url}channel/removeowner/v1", json={
        "token": user4[token],
        "channel_id": channel2[cID],
        "u_id": user2[AuID]}
    )

    assert response5.status_code == 403
    

def test_http_channel_messages(user1, user2):

    #Create private channel by user1
    response = requests.post(f"{url}channels/create/v2", json={
        "token": user1[token],
        "name": "channel1",
        "is_public": False,
    })
    channel1 = response.json()
    
    
    #channel ID not a valid channel 
    invalid_cID = -1
    invalid_channel = requests.get(f"{url}channel/messages/v2", params = {
        'token': user1[token],
         cID: invalid_cID, 
        "start": "0"
    })
    assert invalid_channel.status_code == 400
    
    #when start is greater than # of messages in channel
    invalid_start = requests.get(f"{url}channel/messages/v2", params = {
        "token": user1[token],
        cID: channel1[cID],
        'start': 2,
    })
    assert invalid_start.status_code == 400  
    
    
    #Access error when authorised user not a member of channel 
    access_error = requests.get(f"{url}channel/messages/v2", params = {
        "token": user2[token],
        cID: channel1[cID],
        'start': 0,
    })
    assert access_error.status_code == 403 
    
def test_http_channel_messages_valid(user1, user2):
    # Create first channel for first test case
    # Success case 1: Less than 50 messages returns end as -1 
    channel1 = requests.post(f"{url}channels/create/v2", json={
        "token": user1[token],
        "name": "channel1",
        "is_public": False,
    }).json()
    requests.post(f"{url}message/send/v2", json = {
            "token": user1[token],
            cID: channel1[cID],
            "message" : "First message",
        })

    result1 = requests.get(f"{url}channel/messages/v2", params = {
        "token": user1[token],
        cID: channel1[cID],
        'start': 0
    }).json()

    assert len(result1['messages']) == 1
    assert result1['start'] == 0
    assert result1['end'] == -1

    # Success case 2: 50 messages returns end as -1 
    message_counter = 1
    for _ in range(50):
        requests.post(f"{url}message/send/v2", json = {
            "token": user1[token],
            cID: channel1[cID],
            "message" : f"{message_counter}",
        })
        message_counter +=1

    result2 = requests.get(f"{url}channel/messages/v2", params = {
        "token": user1[token],
        cID: channel1[cID],
        'start': 1
    }).json()

    assert len(result2['messages']) == 50
    assert result2['start'] == 1
    assert result2['end'] == -1

    # Success case 3: 51 messages returns end as 50 (more messages to load)
    channel2 = requests.post(f"{url}channels/create/v2", json={
        "token": user2[token],
        "name": "Second",
        "is_public": True,
    }).json()

    message_counter = 1
    for _ in range(51):
        requests.post(f"{url}message/send/v2", json = {
            "token": user2[token],
            cID: channel2[cID],
            "message" : f"{message_counter}",
        })
        message_counter +=1

    result3 = requests.get(f"{url}channel/messages/v2", params = {
        "token": user1[token],
        cID: channel1[cID],
        'start': 0
    }).json()

    assert len(result3['messages']) == 50
    assert result3['start'] == 0
    assert result3['end'] == 50
