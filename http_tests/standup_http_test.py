#File for http testing of standup functions 

import pytest
from src.config import url
from src.standup import standup_start_v1, standup_active_v1, standup_send_v1
from src.error import InputError, AccessError
from src.other import SECRET, clear_v1
import src.channel
from src.channel import channel_messages_v1
import jwt
import json
import time
import requests 
from datetime import datetime, timezone 

AuID     = 'auth_user_id'
uID      = 'u_id'
cID      = 'channel_id'
chans    = 'channels'
token    = 'token'
standard_length = 1 

@pytest.fixture
def invalid_token():
    return jwt.encode({'session_id': -1, 'user_id': -1}, SECRET, algorithm='HS256')

@pytest.fixture
def user1():
    clear_v1()    
    return src.auth.auth_register_v2("first@gmail.com", "password", "User", "1")

@pytest.fixture
def user2():
    return src.auth.auth_register_v2("second@gmail.com", "password", "User", "2")

@pytest.fixture
def user3():
    return src.auth.auth_register_v2("third@gmail.com", "password", "User", "3")

#HTTP test that when channel ID is invalid standup_start_v1 returns an InputError
def test_http_standup_start_v1_invalid_cID(user1):
    invalid_cID = -1
    response = requests.post(f"{url}standup/start/v1", json={
        token: user1[token],
        cID: invalid_cID,
        'length': 1
    })
    assert response.status_code == 400

#HTTP test that when there is an active standup running in the channel standup_start_v1 returns an InputError
def test_http_standup_start_v1_active_standup(user1):
    response = requests.post(f"{url}channels/create/v2", json={
        "token": user1[token],
        "name": "Channel1",
        "is_public": True
    })
    channel = response.json()
    
    requests.post(f"{url}standup/start/v1", json={
        token: user1[token],
        cID: channel[cID],
        'length': standard_length 
    })
    
    #Start standup when standup is already active 
    response2 = requests.post(f"{url}standup/start/v1", json={
        token: user1[token],
        cID: channel[cID],
        'length': standard_length
    })
    assert response2.status_code == 400
    
#HTTP test that access error raise when authorised user not in the channel for standup_start_v1
def test_http_standup_start_v1_user_not_in(user1, user2):
    response = requests.post(f"{url}channels/create/v2", json={
        "token": user1[token],
        "name": "Channel1",
        "is_public": False
    })
    channel = response.json()
    
    response = requests.post(f"{url}standup/start/v1", json={
        token: user2[token],
        cID: channel[cID],
        'length': standard_length
    })
    assert response.status_code == 403

#HTTP test that starting a standup behaves as specified 
def test_http_standup_start_v1(user1):
    response = requests.post(f"{url}channels/create/v2", json={
        token: user1[token],
        "name": "Channel1",
        "is_public": False
    })
    channel = response.json()

    response = requests.post(f"{url}standup/start/v1", json={
        token: user1[token],
        cID: channel[cID],
        "length": standard_length
    })
    
    standup = response.json()
    #Assert that time_finish is correct 
    now = datetime.now()
    time_finish = int(now.strftime("%s")) + standard_length 
    assert standup['time_finish'] == time_finish
    
#HTTP test that standup_active_v1 raises an InputError when channel ID is invalid 
#Assumption, don't have to be in channel to call standup_active_v1
def test_http_standup_active_v1_invalid_cID(user1):
    invalid_cID = -1
    response = requests.get(f"{url}standup/active/v1", params={
        token: user1[token],
        cID: invalid_cID,
        "length": standard_length
    })
    assert response.status_code == 400
    
#HTTP test that standup_active_v1 behaves as specified 
def test_http_standup_active_v1(user1):
    response = requests.post(f"{url}channels/create/v2", json={
        token: user1[token],
        "name": "Channel",
        "is_public": False
    })
    channel = response.json()
    
    requests.post(f"{url}standup/start/v1", json={
        token: user1[token],
        cID: channel[cID],
        "length": standard_length
    })
    
    response2 = requests.get(f"{url}standup/active/v1", params={
        token: user1[token],
        cID: channel[cID],
    })
    standup = response2.json()
    #Check that standup is active
    assert standup['is_active']
    #return of time_finish is correct 
    now = datetime.now()
    time_finish = int(now.strftime("%s")) + standard_length 
    assert standup['time_finish'] == time_finish

    #Check that after length standup is no longer active 
    time.sleep(standard_length)
    response3 = requests.get(f"{url}standup/active/v1", params={
        token: user1[token],
        cID: channel[cID],
    })
    standup_end = response3.json()
    assert not standup_end['is_active']
    
#HTTP test that threading and timers done correctly for standup_active_v1
def test_http_standup_active_v1_correct_time(user1):
    response = requests.post(f"{url}channels/create/v2", json={
        token: user1[token],
        "name": "Channel1",
        "is_public": False
    })
    channel1 = response.json()

    response2 = requests.post(f"{url}channels/create/v2", json={
        token: user1[token],
        "name": "Channel2",
        "is_public": False
    })
    channel2 = response2.json()
    
    requests.post(f"{url}standup/start/v1", json={
        token: user1[token],
        cID: channel1[cID],
        "length": standard_length
    })
    
    requests.post(f"{url}standup/start/v1", json={
        token: user1[token],
        cID: channel2[cID],
        "length": standard_length * 2
    })
    
    time.sleep(standard_length)
    #Check that threading was done correctly, i.e. fake_channel is still running after standard_length 
    response5 = requests.get(f"{url}standup/active/v1", params={
        token: user1[token],
        cID: channel2[cID],
    })
    standup2 = response5.json()
    assert standup2['is_active']

#HTTP test that InputError raised when cID not valid for standup_send_v1
def test_http_standup_send_v1_invalid_cID(user1):
    invalid_cID = -1
    response = requests.post(f"{url}standup/send/v1", json={
        token: user1[token],
        cID: invalid_cID,
        "message": "Hello"
    })
    assert response.status_code == 400
    
#HTTP test that InputError raised when message more than 1000 characters for standup_send_v1
def test_http_standup_send_v1_invalid_message(user1):
    invalid_message = '?' * 1001 
    response = requests.post(f"{url}channels/create/v2", json={
        "token": user1[token],
        "name": "Channel1",
        "is_public": True
    })
    channel = response.json()
    
    requests.post(f"{url}standup/start/v1", json={
        token: user1[token],
        cID: channel[cID],
        'length': standard_length
    })
    
    response2 = requests.post(f"{url}standup/send/v1", json={
        token: user1[token],
        cID: channel[cID],
        'message': invalid_message
    })
    
    assert response2.status_code == 400

#HTTP test that InputError raised when standup not active for standup_send_v1
def test_http_standup_send_v1_inactive_standup(user1):
    response = requests.post(f"{url}channels/create/v2", json={
        "token": user1[token],
        "name": "Channel1",
        "is_public": True
    })
    channel = response.json()
    response2 = requests.post(f"{url}standup/send/v1", json={
        token: user1[token],
        cID: channel[cID],
        'message': 'Hello'
    })
    assert response2.status_code == 400
    

#HTTP test that AccessError raised when user not a member of channel for standup_send_v1
def test_http_standup_send_v1_invalid_user(user1, user2):
    response = requests.post(f"{url}channels/create/v2", json={
        "token": user1[token],
        "name": "Channel1",
        "is_public": False
    })
    channel = response.json()
    
    response2 = requests.post(f"{url}standup/send/v1", json={
        token: user2[token],
        cID: channel[cID],
        'message': 'Hello'
    })
    assert response2.status_code == 403
    
#HTTP test that messages can be sent within a standup as specified for one message  
def test_http_standup_send_v1_one_message(user1):
    response = requests.post(f"{url}channels/create/v2", json={
        "token": user1[token],
        "name": "Channel1",
        "is_public": False
    })
    channel = response.json()

    requests.post(f"{url}standup/start/v1", json={
        token: user1[token],
        cID: channel[cID],
        'length': standard_length
    })
    
    #Assert that one message can be sent correctly 
    requests.post(f"{url}standup/send/v1", json={
        token: user1[token],
        cID: channel[cID],
        'message': 'Hello'
    })
    
    time.sleep(standard_length)
    response2 = requests.get(f"{url}channel/messages/v2", params={
        "token": user1[token],
        "channel_id": channel[cID],
        "start": 0
    })
    message_list = response2.json()
    assert len(message_list['messages']) == 1
    for messages in message_list['messages']:
        assert "user1: Hello" in messages['message']
        
#HTTP test that messages can be sent within a standup within the correct channel and not other channel 
def test_http_standup_send_v1_correct_channel(user1):
    response = requests.post(f"{url}channels/create/v2", json={
        "token": user1[token],
        "name": "Channel1",
        "is_public": False
    })
    channel = response.json()
    
    #Create fake channel to ensure messages in standup being sent to correct channel
    fake_response = requests.post(f"{url}channels/create/v2", json={
        "token": user1[token],
        "name": "fake_channel",
        "is_public": True
    })
    fake_channel = fake_response.json()  
    
    requests.post(f"{url}standup/start/v1", json={
        token: user1[token],
        cID: channel[cID],
        'length': standard_length
    })
    
    #Make sure message was only sent to correct channel 
    response = requests.get(f"{url}channel/messages/v2", params={
        "token": user1[token],
        "channel_id": fake_channel[cID],
        "start": 0
    })
    message_list = response.json()
    assert len(message_list['messages']) == 0
    for messages in message_list['messages']:
        assert "user1: Hello" not in messages['message']   

#HTTP test messages can be sent within a standup as specified for more than one message 
def test_http_standup_send_v1_multiple_messages(user1, user2):
    response = requests.post(f"{url}channels/create/v2", json={
        "token": user1[token],
        "name": "Channel",
        "is_public": False
    })
    channel = response.json()
    
    requests.post(f"{url}channel/invite/v2", json={
        token: user1[token],
        cID: channel[cID],
        "u_id": user2[AuID]}
    )
    
    requests.post(f"{url}standup/start/v1", json={
        token: user1[token],
        cID: channel[cID],
        'length': standard_length
    })

    requests.post(f"{url}standup/send/v1", json={
        token: user1[token],
        cID: channel[cID],
        'message': 'Hello'
    })

    requests.post(f"{url}standup/send/v1", json={
        token: user2[token],
        cID: channel[cID],
        'message': 'Goodbye'
    })
    
    #After standup is finished 
    time.sleep(standard_length)
    
    response2 = requests.get(f"{url}channel/messages/v2", params={
        "token": user1[token],
        "channel_id": channel[cID],
        "start": 0
    })
    
    message_list = response2.json()
    assert len(message_list['messages']) == 1
    for messages in message_list['messages']:
        assert "user1: Hello\nuser2: Goodbye" in messages['message']
