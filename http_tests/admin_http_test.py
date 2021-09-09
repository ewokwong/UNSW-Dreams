import pytest
import requests
import json
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
        "name_last": "1",
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

def test_http_admin_user_remove_valid(user1, user2):

    chan = requests.post(f"{url}channels/create/v2", json={
        "token": user1[token],
        "name": "Channel",
        "is_public": True
    })
    channelTest = chan.json()

    requests.post(f"{url}channel/join/v2", json={
        "token": user2[token],
        "channel_id": channelTest[cID]
    })

    msg = requests.post(f"{url}message/send/v2", json={
        "token": user2[token],
        "channel_id": channelTest[cID],
        "message": 'Hello'
    })
    message = msg.json()

    #* User not an owner
    response_1 = requests.delete(f"{url}admin/user/remove/v1", json={
        "token": user2[token],
        "u_id": user1[AuID]
    })    
    assert response_1.status_code == 403

    requests.delete(f"{url}admin/user/remove/v1", json={
        "token": user1[token],
        "u_id": user2[AuID]
    })    

    msg_data = requests.get(f"{url}channel/messages/v2", params={
        "token": user1[token],
        "channel_id": channelTest[cID],
        "start": 0
    })
    message_data = msg_data.json()

    for dictionary in (message_data['messages']):
        if dictionary['message_id'] == message['message_id']:
            assert 'Removed user' in dictionary['message']

    users_data = requests.get(f"{url}users/all/v1", params={
        "token": user1[token]
    })
    users = users_data.json()

    assert users == {
            'users':
            [{
            'u_id': 0, 
            'email': "first@gmail.com", 
            'name_first': 'User', 
            'name_last': '1', 
            'handle_str': 'user1',
            'profile_img_url': f"{url}static/default.jpg"
            }]
    } 

    #* Test: u_id does not refer to a valid user
    response_2 = requests.delete(f"{url}admin/user/remove/v1", json={
        "token": user1[token],
        "u_id": -1
    })    
    assert response_2.status_code == 400

    #* Test: the user is currently only owner    
    response_3 = requests.delete(f"{url}admin/user/remove/v1", json={
        "token": user1[token],
        "u_id": user1[AuID]
    })    
    assert response_3.status_code == 400

def test_http_userpermissions_change(user1, user2, user3):

    #* Test 1: Test if the user gets the permissions when changed by user1

    requests.post(f"{url}admin/userpermission/change/v1", json={
        "token": user1[token],
        "u_id": user2[AuID],
        "permission_id": 1}
    )

    chan = requests.post(f"{url}channels/create/v2", json={
        "token": user3[token],
        "name": "channel",
        "is_public": False}
    )
    channel = chan.json()

    requests.post(f"{url}channel/join/v2", json={
        "token": user2[token],
        "channel_id": channel[cID]}
    )

    response = requests.get(f"{url}channel/details/v2", params={
        'token': user2[token],
        'channel_id': channel[cID]}
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

    requests.post(f"{url}channel/addowner/v1", json={
        "token": user2[token],
        "channel_id": channel[cID],
        "u_id": user2[AuID]}
    )

    response1 = requests.get(f"{url}channel/details/v2", params={
        'token': user2[token],
        'channel_id': channel[cID]}
    )
    details1 = response1.json()
    assert {
        fName: 'User', 
        lName: '2', 
        'email': "second@gmail.com", 
        'handle_str': "user2",
        uID: user2[AuID],
        'profile_img_url': f"{url}static/default.jpg"
    } in details1[ownMems]


    #* Test 2: Raise input error for invalid permission id
    response2 = requests.post(f"{url}admin/userpermission/change/v1", json={
        "token": user1[token],
        "u_id": user2[AuID],
        "permission_id": -1}
    )

    assert response2.status_code == 400

    #* Test 3: Raise input error for invalid user id
    response3 = requests.post(f"{url}admin/userpermission/change/v1", json={
        "token": user1[token],
        "u_id": 9999,
        "permission_id": 2}
    )
    
    assert response3.status_code == 400

    #* Test 4: Raise Access Error when a non- Dreams owner is change permissions

    response4 = requests.post(f"{url}admin/userpermission/change/v1", json={
        "token": user3[token],
        "u_id": user3[AuID],
        "permission_id": 2}
    )

    assert response4.status_code == 403

