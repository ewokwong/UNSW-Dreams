# File to test functions in src/channel.py

import pytest
from src.channel import channel_invite_v1, channel_details_v1, channel_messages_v1, channel_leave_v1, channel_join_v1, channel_addowner_v1, channel_removeowner_v1
import src.auth, src.channels, src.other
from src.error import InputError, AccessError
from src.channels import channels_create_v1, channels_list_v2
from src.message import message_send_v1
import jwt
from src.other import SECRET
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

def test_channel_invite(user1, user2, user3):

    privateChannel = src.channels.channels_create_v1(user1[token], 'Coolkids', False)

    #* Test 1: Does user2 get successfully invited to channel "Coolkids"
    channel_invite_v1(user1[token], privateChannel[cID], user2[AuID])
    assert {
        fName: 'User', 
        lName: '2', 
        'email': "second@gmail.com", 
        'handle_str': "user2",
        'profile_img_url': f"{url}static/default.jpg",
        uID: user2[AuID],
    } in channel_details_v1(user1[token], privateChannel[cID])[allMems]
    
    #* Test 2: is InputError raised when cID does not refer to valid channel
    with pytest.raises(InputError):
        channel_invite_v1(user1[token], "ThischannelIDdoesNotExist", user2[AuID])
    
    #* Test 3: is InputError raised when u_id isnt a valid user
    with pytest.raises(InputError):
        channel_invite_v1(user1[token], "ThischannelIDdoesNotExist", "DoesntExist")
    
    #* Test 4: is AccessError raised when auth_uID is not already a member of the channel
    with pytest.raises(AccessError):
        channel_invite_v1(user3[token], privateChannel[cID], user2[AuID])


def test_channel_details(user1, user2):

    realChannel = src.channels.channels_create_v1(user1[token], 'ChannelINFO', True)

    #* Test 1: Using the authorised user, does the channel details get presented for one user in channel
    
    assert channel_details_v1(user1[token], realChannel[cID]) == {
        'name': "ChannelINFO",
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
    
    #* Test 2: Is InputError raised when Channel ID is not a valid channel
    with pytest.raises(InputError):
        channel_details_v1(user1[token], 'InvalidID')

    #* Test 3: Is AccessError raised when the user is not membber of channel with the channel id
    with pytest.raises(AccessError):
        channel_details_v1(user2[token], realChannel[cID])

def test_channel_messages_errors(user1, user2):
    firstChannel = channels_create_v1(user1[token], 'Yggdrasil', False)
    #* Test 1: returns input error when start is greater than total number of messages in channel
    with pytest.raises(InputError):
        channel_messages_v1(user1[token], firstChannel[cID], 4)

    #* Test 2: Raises input error when channel_id is invalid 
    invalid_channel_id = -1
    with pytest.raises(InputError):
        channel_messages_v1(user1[token], invalid_channel_id, 0)

    #* Test 3: returns access error when authorised user not a member of channel
    with pytest.raises(AccessError):
        channel_messages_v1(user2[token], firstChannel[cID], 0)

def test_channel_messages(user1, user2):
    #Create private channel by userID1
    firstChannel = channels_create_v1(user1[token], 'Yggdrasil', False)
    message_send_v1(user1[token], firstChannel[cID], "First Message")
    
    # Success case 1: if there are less than 50 messages, returns -1 in "end"
    assert len(channel_messages_v1(user1[token], firstChannel[cID], 0)["messages"]) == 1
    assert channel_messages_v1(user1[token], firstChannel[cID], 0)["start"] == 0
    assert channel_messages_v1(user1[token], firstChannel[cID], 0)["end"] == -1
    
    # Success case 2: if there are 50 messages, returns -1 in "end"
    secondChannel = channels_create_v1(user2[token], 'Second', False)
    for _ in range(50):
        message_send_v1(user2[token], secondChannel[cID], "xD")
    assert len(channel_messages_v1(user2[token], secondChannel[cID], 0)["messages"]) == 50
    assert channel_messages_v1(user2[token], secondChannel[cID], 0)["start"] == 0
    assert channel_messages_v1(user2[token], secondChannel[cID], 0)["end"] == -1

    # Success case 3: if there are 51 messages, returns "start" + 1 in "end"
    for _ in range(50):
        message_send_v1(user1[token], firstChannel[cID], "xD")
    assert len(channel_messages_v1(user1[token], firstChannel[cID], 0)["messages"]) == 50
    assert channel_messages_v1(user1[token], firstChannel[cID], 0)["start"] == 0
    assert channel_messages_v1(user1[token], firstChannel[cID], 0)["end"] == 50

def test_channel_leave(user1, user2, user3, user4):

    #* user1 made public channel 'TrumpPence'
    firstChannel = src.channels.channels_create_v1(user1[token], 'TrumpPence', True)

    #* user2, user3 and user4 join public channel 'TrumpPence'
    channel_join_v1(user2[token], firstChannel[cID])
    channel_join_v1(user3[token], firstChannel[cID])
    channel_join_v1(user4[token], firstChannel[cID])

    #* Make sure they joined
    assert {
        uID: user2[AuID],
        fName: 'User',
        lName: "2",
        'email': "second@gmail.com",
        'handle_str': "user2",
        'profile_img_url': f"{url}static/default.jpg"
    } in channel_details_v1(user2[token], firstChannel[cID])[allMems]
    assert {
        uID: user3[AuID],
        fName: 'User',
        lName: "3",
        'email': "third@gmail.com",
        'handle_str': "user3",
        'profile_img_url': f"{url}static/default.jpg"
    } in channel_details_v1(user3[token], firstChannel[cID])[allMems]
    assert {
        uID: user4[AuID],
        fName: 'User',
        lName: "4",
        'email': "fourth@gmail.com",
        'handle_str': "user4",
        'profile_img_url': f"{url}static/default.jpg"
    } in channel_details_v1(user4[token], firstChannel[cID])[allMems]

    #* One of them gets removed
    channel_leave_v1(user3[token], firstChannel[cID])
    assert {
        uID: user3[token],
        fName: 'User',
        lName: "3",
        'email': "third@gmail.com",
        'handle_str': "user3",
        'profile_img_url': f"{url}static/default.jpg"
    } not in channel_details_v1(user1[token], firstChannel[cID])[allMems]

    #* Another gets removed 
    channel_leave_v1(user4[token], firstChannel[cID])
    assert {
        uID: user4[token],
        fName: 'User',
        lName: "4",
        'email': "fourth@gmail.com",
        'handle_str': "user4",
        'profile_img_url': f"{url}static/default.jpg"
    } not in channel_details_v1(user1[token], firstChannel[cID])[allMems]


    #* Test if someone not in the group cannot 'leave' the group
    with pytest.raises(AccessError):
        channel_leave_v1(user3[token], firstChannel[cID])

    #* Test you cannot leave a channel that doesn't exist
    with pytest.raises(InputError):
        channel_leave_v1(user3[token], -1)

    #* Finished testing for this function
    #! Clearing data
    src.other.clear_v1()


def test_channel_join(user1, user2, user3, user4):

    # user1 made public channel 'TrumpPence'
    firstChannel = src.channels.channels_create_v1(user1[token], 'TrumpPence', True)
    # user2 made private channel 'BidenHarris'
    secondChannel = src.channels.channels_create_v1(user2[token], 'BidenHarris', False)

    #* Test 1: If user3 successfully joins public channel 'TrumpPence'
    channel_join_v1(user3[token], firstChannel[cID])
    assert {
        uID: user3[AuID],
        'email': "third@gmail.com",
        fName: "User",
        lName: "3",
        'handle_str': 'user3',
        'profile_img_url': f"{url}static/default.jpg"
    } in channel_details_v1(user3[token], firstChannel[cID])[allMems]

    #* Test 2: If user4 unsuccessfully joins private channel 'BidenHarris'
    with pytest.raises(AccessError): 
        # Check if AccessError is raised when trying to join a private channel
        channel_join_v1(user4[token], secondChannel[cID])

    #* Test 3: user3 and user4 aren't in channels they haven't joined 
    with pytest.raises(AccessError):
        channel_details_v1(user3[token], secondChannel[cID])[allMems]
        channel_details_v1(user4[token], firstChannel[cID])[allMems]

    #* Test 4: Check if InputError is raised when channel does not exist
    #! Clearing data
    src.other.clear_v1()                                    # Channel is deleted
    with pytest.raises(InputError):                         
        channel_join_v1(user1[token], firstChannel[cID])   # user1 tries to join the non-existent channel

    #* Finished testing for this function
    #! Clearing data
    #   src.other.clear_v1()

def test_channel_addowner(user1,user2,user3,user4,user5):

    channelTest = src.channels.channels_create_v1(user2[token], 'Channel', False)

    # Test 1: Testing for whether added user now appears in both owner list and all members list of private chan
    channel_addowner_v1(user2[token], channelTest[cID], user3[AuID])
    assert {
        uID: user3[AuID],        
        fName: 'User',
        lName: '3',
        'email': 'third@gmail.com',
        'handle_str': 'user3',
        'profile_img_url': f"{url}static/default.jpg"
    } in channel_details_v1(user2[token], channelTest[cID])[ownMems]
    assert {
        uID: user3[AuID],
        fName: 'User',
        lName: '3',
        'email': 'third@gmail.com',
        'handle_str': 'user3',
        'profile_img_url': f"{url}static/default.jpg"
    } in channel_details_v1(user2[token], channelTest[cID])[allMems]

    channelTest2 = src.channels.channels_create_v1(user1[token], 'Channel2', True)

    # Test 2: Testing for whether added user now appears in both owner list and all members list of public chan
    channel_addowner_v1(user1[token], channelTest2[cID], user3[AuID])
    assert {
        uID: user3[AuID],
        fName: 'User',
        lName: '3',
        'email': 'third@gmail.com',
        'handle_str': 'user3',
        'profile_img_url': f"{url}static/default.jpg"
    } in channel_details_v1(user3[token], channelTest2[cID])[ownMems]
    assert {
        uID: user3[AuID],
        fName: 'User',
        lName: '3',
        'email': 'third@gmail.com',
        'handle_str': 'user3',
        'profile_img_url': f"{url}static/default.jpg"
    } in channel_details_v1(user3[token], channelTest2[cID])[allMems]

    # Test 3: for invalid channel, raising input error
    with pytest.raises(InputError): 
        channel_addowner_v1(user2[token], 999, user4[AuID])
    
    # Test 4: for user already in owner list
    with pytest.raises(InputError):
        channel_addowner_v1(user2[token], channelTest[cID], user3[AuID])

    # Test 5: User with no permission to add owner
    with pytest.raises(AccessError):
        channel_addowner_v1(user4[token], channelTest[cID], user5[AuID])
    
        

def test_channel_removeowner(user1, user2, user3, user4):

    channelTest = src.channels.channels_create_v1(user2[token], 'Channel5', True)
    channelTest2 = src.channels.channels_create_v1(user3[token], 'Channel6', True)
    
    # Test 1: adding a owner into channel and testing if they are successfully removed
    channel_addowner_v1(user2[token], channelTest[cID], user3[AuID])
    channel_addowner_v1(user2[token], channelTest[cID], user4[AuID])
    channel_removeowner_v1(user3[token], channelTest[cID], user4[AuID])
    # check to see if user2 has been removed from owners, but remains in all members
    assert {
        uID: user3[AuID],
        fName: 'User',
        lName: '3',
        'email': 'third@gmail.com',
        'handle_str': 'user3',
        'profile_img_url': f"{url}static/default.jpg"
    } in channel_details_v1(user2[token], channelTest[cID])[ownMems]
    assert {
        uID: user3[AuID],
        fName: 'User',
        lName: '3',
        'email': 'third@gmail.com',
        'handle_str': 'user3',
        'profile_img_url': f"{url}static/default.jpg"
    } in channel_details_v1(user2[token], channelTest[cID])[allMems]
    assert{
        uID: user4[AuID],
        fName: 'User',
        lName: '4',
        'email': 'fourth@gmail.com',
        'handle_str': 'user4',
        'profile_img_url': f"{url}static/default.jpg"
    } in channel_details_v1(user2[token], channelTest[cID])[allMems]

    # Test 2: with an invalid Channel ID, tests for Input Error being raised
    with pytest.raises(InputError):
        channel_removeowner_v1(user3[token], 9999, user2[AuID])

    # Test 3: Raise Input error successful for user not in the owner members
    with pytest.raises(InputError):
        channel_removeowner_v1(user3[token], channelTest[cID], user4[AuID])
    
    # Test 4: With only one member in owner left, does not remove them, raising input error
    with pytest.raises(InputError):
        channel_removeowner_v1(user3[token], channelTest2[cID], user3[AuID])

    # Test 5: Non-owner trying to remove, raising access Error
    channel_addowner_v1(user3[token], channelTest2[cID], user4[AuID])
    with pytest.raises(AccessError):
        channel_removeowner_v1(user2[token], channelTest2[cID], user3[AuID])
