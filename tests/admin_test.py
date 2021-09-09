# File to test functions in src/admin.py
import pytest
from src.admin import user_remove_v1, userpermission_change_v1
from src.error import AccessError, InputError
from src.other import SECRET
import src.channel, src.channels, src.auth, src.dm, src.message, src.other, src.user
import jwt
import json
from src.config import url

AuID    = 'auth_user_id'
uID     = 'u_id'
cID     = 'channel_id'
chans   = 'channels'
allMems = 'all_members'
ownMems = 'owner_members'
fName   = 'name_first'
lName   = 'name_last'
token   = 'token'

@pytest.fixture
def user1():
    src.other.clear_v1()    
    return src.auth.auth_register_v2("first@gmail.com", "password", "User", "1")

@pytest.fixture
def user2():
    return src.auth.auth_register_v2("second@gmail.com", "password", "User", "2")

@pytest.fixture
def user3():
    return src.auth.auth_register_v2("third@gmail.com", "password", "User", "3")

@pytest.fixture
def user4():
    return src.auth.auth_register_v2("fourth@gmail.com", "password", "User", "4")

@pytest.fixture
def user5():
    return src.auth.auth_register_v2("fifth@gmail.com", "password", "User", "5")

def test_user_remove(user1, user2, user3):
    
    channelTest = src.channels.channels_create_v1(user1[token], 'Channel', True)
    channelTest2 = src.channels.channels_create_v1(user1[token], 'Channel2', True)
    src.channel.channel_join_v1(user2[token], channelTest2[cID])
    src.channel.channel_join_v1(user2[token], channelTest[cID])
    message = src.message.message_send_v1(user2[token], channelTest[cID], 'Hello')
    src.message.message_send_v1(user1[token], channelTest[cID], 'Hi')
    src.channel.channel_addowner_v1(user1[token], channelTest[cID], user3[AuID])
    src.dm.dm_create_v1(user1[token], [user2[AuID]])
    src.dm.dm_create_v1(user2[token], [user3[AuID]])
    #* User not an owner
    with pytest.raises(AccessError): 
        user_remove_v1(user2[token], user1[AuID])
    

    user_remove_v1(user1[token], user2[AuID])
    user_remove_v1(user1[token], user3[AuID])
    for dictionary in (src.channel.channel_messages_v1(user1[token], channelTest[cID], 0)['messages']):
        if dictionary['message_id'] == message['message_id']:
            assert 'Removed user' in dictionary['message']

    users = src.user.users_all(user1[token])
    assert users == {
            'users':
            [{
            'u_id': 0, 
            'email': "first@gmail.com", 
            'name_first': 'User', 
            'name_last': '1', 
            'handle_str': 'user1',
            'profile_img_url': f"{url}static/default.jpg"
            },]
    } 
    with pytest.raises(InputError):
        src.channel.channel_invite_v1(user1['token'], channelTest['channel_id'], user2[AuID])
    
    #* Test: u_id does not refer to a valid user
    with pytest.raises(InputError):
        user_remove_v1(user1[token], -1)

    #* Test: the user is currently only owner
    with pytest.raises(InputError): 
        user_remove_v1(user1[token], user1[AuID])

def test_userpermissions_change(user1, user2, user3):

    #* Test 1: Test if the user gets the permissions when changed by user1
    userpermission_change_v1(user1[token], user2[AuID], 1)

    channelTest = src.channels.channels_create_v1(user3[token], 'Channel', False)

    src.channel.channel_join_v1(user2[token], channelTest[cID])

    # using Owner only permissions, test if permissions work
    #* Test 2: Join private channel
    assert {
        uID: user2[AuID],        
        fName: 'User',
        lName: '2',
        'email': 'second@gmail.com',
        'handle_str': 'user2',
        'profile_img_url': f"{url}static/default.jpg"
    } in src.channel.channel_details_v1(user2[token], channelTest[cID])[allMems]

    #* Test 3: adding owner when user is not an owner of the channel but has dreams permissions
    assert {
        uID: user2[AuID],        
        fName: 'User',
        lName: '2',
        'email': 'second@gmail.com',
        'handle_str': 'user2',
        'profile_img_url': f"{url}static/default.jpg"
    } in src.channel.channel_details_v1(user2[token], channelTest[cID])[ownMems]

    src.channel.channel_removeowner_v1(user2[token], channelTest[cID], user3[AuID])

    #* Test 4: Removing owner when user2 has Dreams owner permissions
    assert {
        uID: user3[AuID],        
        fName: 'User',
        lName: '3',
        'email': 'third@gmail.com',
        'handle_str': 'user3',
        'profile_img_url': f"{url}static/default.jpg"
    } not in src.channel.channel_details_v1(user2[token], channelTest[cID])[ownMems]

    assert {
        uID: user3[AuID],        
        fName: 'User',
        lName: '3',
        'email': 'third@gmail.com',
        'handle_str': 'user3',
        'profile_img_url': f"{url}static/default.jpg"
    } in src.channel.channel_details_v1(user2[token], channelTest[cID])[allMems]

    #* Test 5: Raise input error for invalid permission id
    with pytest.raises(InputError):
        userpermission_change_v1(user1[token], user2[AuID], -1)
    
    #* Test 6: Raise input error for invalid user id
    with pytest.raises(InputError):
        userpermission_change_v1(user1[token], 9999, 0)

    #* Test 7: Raise Access Error when a non- Dreams owner is changing permissions
    with pytest.raises(AccessError):
        userpermission_change_v1(user3[token], user3[token], 2)