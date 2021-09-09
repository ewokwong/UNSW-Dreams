import pytest
from src.channels import channels_list_v2, channels_listall_v2, channels_create_v1
from src.error import AccessError, InputError
import src.auth, src.channel, src.other
from src.other import clear_v1, SECRET
import jwt

AuID    = 'auth_user_id'
uID     = 'u_id'
cID     = 'channel_id'
allMems = 'all_members'
Name    = 'name'
fName   = 'name_first'
lName   = 'name_last'
chans   = 'channels'
token   = 'token'

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

@pytest.fixture
def user4():
    return src.auth.auth_register_v2("fourth@gmail.com", "password", "User", "4")

@pytest.fixture
def user5():
    return src.auth.auth_register_v2("fifth@gmail.com", "password", "User", "5")

#* Test that for invalid tokens, an AccessError is raised
def test_channels_unauthorised_user(invalid_token):
    with pytest.raises(AccessError):
        channels_list_v2(invalid_token)

    with pytest.raises(AccessError):
        channels_listall_v2(invalid_token)

#* Test that running channels_list with valid inputs has the correct returns
def test_channels_list_none(user1, user2):
    channel = channels_create_v1(user1[token], 'Oogway', True)

    assert channels_list_v2(user1[token]) == {
        'channels': [{cID: channel[cID], Name: 'Oogway'}]
    }
    
    assert channels_list_v2(user2[token]) == {
        'channels': []
    }

#* Test that when users are join and leave channels, their channels_list change
def test_channels_list_join_leave(user1, user2, user3):
    channel = channels_create_v1(user1[token], 'Oogway', True)

    assert channels_list_v2(user2[token]) == {
        'channels': []
    }
    
    src.channel.channel_join_v1(user2[token], channel[cID])

    assert channels_list_v2(user2[token]) == {
        'channels': [{cID: channel[cID], Name: 'Oogway'}]
    }

    src.channel.channel_leave_v1(user2[token], channel[cID])

    assert channels_list_v2(user2[token]) == {
        'channels': []
    }

#* Test that the function outputs as expected
def test_channels_listall_valid(user1, user2):
    channel = channels_create_v1(user1[token], 'Oogway', True)
    
    assert channels_listall_v2(user1[token]) == {
        'channels': [{cID: channel[cID], Name: 'Oogway'}]
    }

    assert channels_listall_v2(user2[token]) == {
        'channels': [{cID: channel[cID], Name: 'Oogway'}]
    }

#* Test that private channels are also displayed
def test_channels_listall_private(user1, user2):
    channel = channels_create_v1(user1[token], 'NEZ', False)
    
    assert channels_listall_v2(user2[token]) == {
        'channels': [{cID: channel[cID], Name: 'NEZ'}]
    }

def test_channels_create(user1, user2):

    #* Test 1: Newly created public channel by user1 appears in both of his channel list
    firstChannel = channels_create_v1(user1[token], 'Oogway', True)
    assert {cID: firstChannel[cID], Name: 'Oogway'} in channels_list_v2(user1[token])[chans]
    assert {cID: firstChannel[cID], Name: 'Oogway'} in channels_listall_v2(user1[token])[chans]

    #* Test 2: Make sure this channel doesn't appear in user2's channel list, but does in listall
    assert {cID: firstChannel[cID], Name: 'Oogway'} not in channels_list_v2(user2[token])[chans]
    assert {cID: firstChannel[cID], Name: 'Oogway'} in channels_listall_v2(user2[token])[chans]

    #* Test 3: Newly created private channel by user2 appears in his channel list
    secondChannel = channels_create_v1(user2[token], 'Yayot', False)
    assert {cID: secondChannel[cID], Name: 'Yayot'} in channels_list_v2(user2[token])[chans]
    assert {cID: secondChannel[cID], Name: 'Yayot'} in channels_listall_v2(user2[token])[chans]

    #* Test 4: Make sure this channel doesn't appear in of user1's channel lists
    assert {cID: secondChannel[cID], Name: 'Yayot'} not in channels_list_v2(user1[token])[chans]
    assert {cID: secondChannel[cID], Name: 'Yayot'} in channels_listall_v2(user1[token])[chans]

    #* Test 5: InputError is raised when the channel name is more than 20 chars
    with pytest.raises(InputError):
        channels_create_v1(user1[token], 'abcdefghijklmnopqrstuvwxyz', True)

    #* Finished testing for this function
    #! Clearing data
    clear_v1()