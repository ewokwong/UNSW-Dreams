# file to test functions in src/message.py
import pytest
from src.message import message_send_v1, message_remove_v1, message_edit_v1, message_share_v1, message_senddm_v1, message_pin_v1, message_unpin_v1, message_react_v1, message_unreact_v1
from src.error import InputError, AccessError
import src.channel, src.channels, src.auth, src.dm
from src.other import clear_v1, SECRET
from datetime import timezone, datetime
import jwt
import time


AuID     = 'auth_user_id'
uID      = 'u_id'
cID      = 'channel_id'
chans    = 'channels'
allMems  = 'all_members'
ownMems  = 'owner_members'
fName    = 'name_first'
lName    = 'name_last'
token    = 'token'
mID      = 'message_id'
dmID     = 'dm_id'
Name     = 'name'
thumbsUp = 1
rID      = 'react_id'

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


# message_send_v1
# When message is >1000 characters, InputError is raised
# When authorised user is not part of the channel that they are trying to post in, AccessError is raised
# After the function is sucessfully run, ensure that the return value is correct
def test_message_send(user1, user2, user3, user4):

    # user1 made public channel 'TrumpPence'
    firstChannel = src.channels.channels_create_v1(user1[token], 'TrumpPence', True)

    #* user2 and user3 join public channel 'TrumpPence'
    src.channel.channel_join_v1(user2[token], firstChannel[cID])
    src.channel.channel_join_v1(user3[token], firstChannel[cID])

    #* Test if a super large message raises an InputError
    message = ''
    for _ in range(1500):
        message += '?'
    with pytest.raises(InputError):
        message_send_v1(user1[token], firstChannel[cID], message)

    #* Test if a user not in the channel tries to send a message into the channel
    with pytest.raises(AccessError):
        message_send_v1(user4[token], firstChannel[cID], '?')

    #* Test a message is successfully sent 
    sendOutput = message_send_v1(user1[token], firstChannel[cID], "Hi")
    messageFound = False
    for messageDict in src.channel.channel_messages_v1(user1[token], firstChannel[cID], 0)['messages']:
        if sendOutput['message_id'] == messageDict['message_id']:
            messageFound = True
            break
    assert messageFound is True 

    #* Test another messsage is successfully sent
    sendOutput = message_send_v1(user3[token], firstChannel[cID], "Sup")
    messageFound = False
    for messageDict in src.channel.channel_messages_v1(user1[token], firstChannel[cID], 0)['messages']:
        if sendOutput['message_id'] == messageDict['message_id']:
            messageFound = True
            break
    assert messageFound is True 

    #* All tests passed
    #! Clearing data
    clear_v1()

# message_edit_v1
# When message is >1000 characters, InputError is raised
# If there are no messages with matching message_id, InputError is raised
# Ownership permission tests:
    # Owner of Dreams should be able to edit anything
    # Owner of channels should be able to edit anything in channels they own
    # Non-owner of channels should only be able to edit their own messages
# Test if a message has been edited successfully?
def test_message_edit(user1, user2, user3, user4):

    # user2 made public channel 'TrumpPence'
    firstChannel = src.channels.channels_create_v1(user2[token], 'TrumpPence', True)

    #* user2 and user3 join public channel 'TrumpPence'
    src.channel.channel_join_v1(user1[token], firstChannel[cID])
    src.channel.channel_join_v1(user3[token], firstChannel[cID])
    src.channel.channel_join_v1(user4[token], firstChannel[cID])

    #* user3 sends 4 messages
    message1 = message_send_v1(user3[token], firstChannel[cID], "Yo yo waz poppin'?")
    message2 = message_send_v1(user3[token], firstChannel[cID], "Huh?")
    message3 = message_send_v1(user3[token], firstChannel[cID], "John Cena")
    message4 = message_send_v1(user3[token], firstChannel[cID], "Ricegum")

    #* Test if user1 can edit the message
    message_edit_v1(user1[token], message1['message_id'], 'Jeffrey Meng')
    messageFound = False
    editedMessage = {}
    for messageDict in src.channel.channel_messages_v1(user1[token], firstChannel[cID], 0)['messages']:
        if message1['message_id'] == messageDict['message_id']:
            editedMessage = messageDict
            messageFound = True
            break
    assert messageFound is True 
    assert editedMessage['message'] == 'Jeffrey Meng'
    

    #* Test if user2 can edit the message
    message_edit_v1(user2[token], message2['message_id'], 'Jeffrey Meng')
    messageFound = False
    editedMessage = {}
    for messageDict in src.channel.channel_messages_v1(user2[token], firstChannel[cID], 0)['messages']:
        if message2['message_id'] == messageDict['message_id']:
            editedMessage = messageDict
            messageFound = True
            break
    assert messageFound is True 
    assert editedMessage['message'] == 'Jeffrey Meng'

    #* Test if user3 can edit the message
    message_edit_v1(user3[token], message3['message_id'], 'Jeffrey Meng')
    messageFound = False
    editedMessage = {}
    for messageDict in src.channel.channel_messages_v1(user3[token], firstChannel[cID], 0)['messages']:
        if message3['message_id'] == messageDict['message_id']:
            editedMessage = messageDict
            messageFound = True
            break
    assert messageFound is True 
    assert editedMessage['message'] == 'Jeffrey Meng'

    #* Test if user4 cannot edit the message
    with pytest.raises(AccessError):
        message_edit_v1(user4[token], message4['message_id'], 'Jeffrey Meng')

    #* Test if empty edit removes message
    message_edit_v1(user3[token], message3['message_id'], '')
    messageFound = False
    for messageDict in src.channel.channel_messages_v1(user3[token], firstChannel[cID], 0)['messages']:
        if message3['message_id'] == messageDict['message_id']:
            messageFound = True
            break
    assert messageFound is False

    #* Test if you cannot edit a message that doesn't exist
    with pytest.raises(InputError):
        message_edit_v1(user2[token], -1, "Troll")

    #* Test you cannot edit into a super long message
    tooLong = ""
    for _ in range(1001):
        tooLong += "?"
    with pytest.raises(InputError):
        message_edit_v1(user2[token], message4['message_id'], tooLong) 

    #* Test in dm
    dm1 = src.dm.dm_create_v1(user1[token], [user2[AuID]])
    dmMessage = message_senddm_v1(user1[token], dm1[dmID], "Herp derp")
    with pytest.raises(AccessError):
        message_edit_v1(user2[token], dmMessage['message_id'], 'Jeffrey Meng')

    #* All tests passed
    #! Clearing data
    clear_v1()

# message_remove_v1
# User must be:
    # The user that wrote the message, or
    # The user that owns the channel, or
    # The owner of *Dreams*
# Test if the message is removed??
def test_message_remove(user1, user2, user3, user4):

    # user2 made public channel 'TrumpPence'
    firstChannel = src.channels.channels_create_v1(user2[token], 'TrumpPence', True)

    #* user2 and user3 join public channel 'TrumpPence'
    src.channel.channel_join_v1(user1[token], firstChannel[cID])
    src.channel.channel_join_v1(user3[token], firstChannel[cID])
    src.channel.channel_join_v1(user4[token], firstChannel[cID])

    #* user3 sends 4 messages
    message1 = message_send_v1(user3[token], firstChannel[cID], "Yo yo waz poppin'?")
    message2 = message_send_v1(user3[token], firstChannel[cID], "Huh?")
    message3 = message_send_v1(user3[token], firstChannel[cID], "John Cena")
    message4 = message_send_v1(user3[token], firstChannel[cID], "Ricegum")

    #* Test if user1 can remove the message
    message_remove_v1(user1[token], message1['message_id'])
    messageFound = False
    for messageDict in src.channel.channel_messages_v1(user1[token], firstChannel[cID], 0)['messages']:
        if message1['message_id'] == messageDict['message_id']:
            messageFound = True
            break
    assert messageFound is False
    

    #* Test if user2 can remove the message
    message_remove_v1(user2[token], message2['message_id'])
    messageFound = False
    for messageDict in src.channel.channel_messages_v1(user2[token], firstChannel[cID], 0)['messages']:
        if message2['message_id'] == messageDict['message_id']:
            messageFound = True
            break
    assert messageFound is False

    #* Test if user3 can remove the message
    message_remove_v1(user3[token], message3['message_id'])
    messageFound = False
    for messageDict in src.channel.channel_messages_v1(user3[token], firstChannel[cID], 0)['messages']:
        if message3['message_id'] == messageDict['message_id']:
            messageFound = True
            break
    assert messageFound is False

    #* Test if user4 cannot remove the message
    with pytest.raises(AccessError):
        message_remove_v1(user4[token], message4['message_id'])

    #* Test if you cannot remove a message that doesn't exist
    with pytest.raises(InputError):
        message_remove_v1(user4[token], -1)

    #* Test for dm
    dm1 = src.dm.dm_create_v1(user1[token], [user2[AuID], user3[AuID]])
    dmMessage1 = message_senddm_v1(user2[token], dm1[dmID], "Trigger")
    dmMessage2 = message_senddm_v1(user2[token], dm1[dmID], "Happy")
    #* User 3 cannot remove messages it didn't send
    with pytest.raises(AccessError):
        message_remove_v1(user3[token], dmMessage1[mID])
    #* Dreams owner can remove message
    message_remove_v1(user1[token], dmMessage1[mID])
    messageFound = False
    for messageDict in src.dm.dm_messages_v1(user3[token], dm1[dmID], 0)['messages']:
        if message3['message_id'] == messageDict['message_id']:
            messageFound = True
            break
    assert messageFound is False
    #* User can remove own message
    message_remove_v1(user2[token], dmMessage2[mID])
    messageFound = False
    for messageDict in src.dm.dm_messages_v1(user3[token], dm1[dmID], 0)['messages']:
        if message3['message_id'] == messageDict['message_id']:
            messageFound = True
            break
    assert messageFound is False

def test_message_share_todm(user1, user2, user3, user4):

    channelTest = src.channels.channels_create_v1(user1[token], 'Channel', True)
    src.channel.channel_invite_v1(user1[token], channelTest[cID], user2[AuID])
    dmTest = src.dm.dm_create_v1(user2[token],[user4[AuID],user3[AuID]])
    
    ogMessage = message_send_v1(user1[token],channelTest[cID], "hello jeffrey meng") 

    sharedMessage = message_share_v1(user2[token], ogMessage[mID],'', -1, dmTest[dmID])

    messageFound = False
    for messageDict in src.dm.dm_messages_v1(user2[token],dmTest[dmID],0)['messages']:
        if sharedMessage['shared_message_id'] == messageDict['message_id']:
            messageFound = True
            break
    assert messageFound is True 
    
    # user1 is not in dmTest, raise access error
    with pytest.raises(AccessError):
        message_share_v1(user1[token], ogMessage[mID], '', -1, dmTest[dmID])

def test_message_share_tochannel(user1, user2, user3):

    channelTest = src.channels.channels_create_v1(user1[token], 'Channel', True)
    channelTest2 = src.channels.channels_create_v1(user2[token], 'Channel', True)

    src.channel.channel_invite_v1(user2[token], channelTest2[cID], user1[AuID])
    src.channel.channel_invite_v1(user1[token], channelTest[cID], user3[AuID])

    ogMessage = message_send_v1(user1[token],channelTest[cID], "hello jeffrey meng") 

    sharedMessage = message_share_v1(user1[token], ogMessage[mID],'vincent', channelTest2[cID], -1)

    messageFound = False
    for messageDict in src.channel.channel_messages_v1(user2[token],channelTest2[cID],0)['messages']:
        if sharedMessage['shared_message_id'] == messageDict['message_id']:
            messageFound = True
    assert messageFound is True 

    with pytest.raises(AccessError):
        message_share_v1(user3[token], ogMessage[mID], '', channelTest2[cID], -1)

def test_message_share_dmtodm(user1,user2,user3,user4):
    
    dmTest = src.dm.dm_create_v1(user2[token],[user4[AuID],user3[AuID]])
    dmTest2 = src.dm.dm_create_v1(user1[token],[user2[AuID]])
    
    ogMessage = message_senddm_v1(user1[token], dmTest2[dmID], 'hello meng')

    sharedMessage = message_share_v1(user2[token], ogMessage[mID],'wow', -1, dmTest[dmID])
    messageFound = False
    for messageDict in src.dm.dm_messages_v1(user4[token],dmTest[dmID],0)['messages']:
        if sharedMessage['shared_message_id'] == messageDict['message_id']:
            messageFound = True

    assert messageFound is True 

    with pytest.raises(AccessError):
        message_share_v1(user1[token], ogMessage[mID], '', -1, dmTest[dmID])

#* Test send functions together with message/send/v2
#? Test if message_id increases correctly

def test_senddm_access_error(user1, user2, user3):
    dm1 = src.dm.dm_create_v1(user1[token], [user2[AuID]])
    
    with pytest.raises(AccessError):
        message_senddm_v1(user3[token], dm1[dmID], '')

def test_senddm_long(user1, user2):
    message = ''
    for _ in range(1500):
        message += 'a'
    dm1 = src.dm.dm_create_v1(user1[token], [user2[AuID]])
    
    with pytest.raises(InputError):
        message_senddm_v1(user1[token], dm1[dmID], message)

def test_senddm_invalid_dm(user1):
    invalid_dm_id = -1

    with pytest.raises(InputError):
        message_senddm_v1(user1[token], invalid_dm_id, '')

def test_senddm_multiple(user1, user2):
    dm1 = src.dm.dm_create_v1(user1[token], [user2[AuID]])
    message1 = message_senddm_v1(user1[token], dm1[dmID], '')
    assert message1 == {'message_id': message1['message_id']}

    message2 = message_senddm_v1(user2[token], dm1[dmID], '')
    assert message2 == {'message_id': message2['message_id']}

    message3 = message_senddm_v1(user2[token], dm1[dmID], '')
    assert message3 == {'message_id': message3['message_id']}

def test_dm_unauthorised_user(user1, user2, invalid_token):
    #* All unauthorised user tests
    dm1 = src.dm.dm_create_v1(user1[token], [user2[AuID]])
    
    with pytest.raises(AccessError):
        message_senddm_v1(invalid_token, dm1[dmID], '')

#* Testing that a valid message is pinned for channel
def test_message_pin_valid_channel(user1):
    channel = src.channels.channels_create_v1(user1[token], 'Midsummer Madness', True)
    message_send_v1(user1[token], channel[cID], 'Thumb it to summit')
    target = message_send_v1(user1[token], channel[cID], 'Pin it to win it')
    not_pinned = src.channel.channel_messages_v1(user1[token], channel[cID], 0)
    
    mID_found = False
    for message in not_pinned['messages']:
        if target[mID] == message[mID]:
            mID_found = True
        assert message['is_pinned'] is False
    assert mID_found is True
    
    message_pin_v1(user1[token], target[mID])
    pinned = src.channel.channel_messages_v1(user1[token], channel[cID], 0)
    
    mID_found = False
    for message in pinned['messages']:
        if target[mID] == message[mID]:
            mID_found = True
            assert message['is_pinned'] is True
        else:
            assert message['is_pinned'] is False
    assert mID_found is True

#* Testing that a valid message is pinned for DM
def test_message_pin_valid_dm(user1, user2):
    dm = src.dm.dm_create_v1(user1[token], [user2[AuID]])
    message_senddm_v1(user1[token], dm[dmID], 'Thumb it to summit')
    target = message_senddm_v1(user1[token], dm[dmID], 'Pin it to win it')
    not_pinned = src.dm.dm_messages_v1(user1[token], dm[dmID], 0)
    
    mID_found = False
    for message in not_pinned['messages']:
        if target[mID] == message[mID]:
            mID_found = True
        assert message['is_pinned'] is False
    assert mID_found is True
    
    message_pin_v1(user1[token], target[mID])
    pinned = src.dm.dm_messages_v1(user1[token], dm[dmID], 0)
    
    mID_found = False
    for message in pinned['messages']:
        if target[mID] == message[mID]:
            mID_found = True
            assert message['is_pinned'] is True
        else:
            assert message['is_pinned'] is False
    assert mID_found is True

#* Test that an InputError is raised when the message_id is invalid
def test_message_pin_invalid_mID(user1):
    invalid_mID = -1
    with pytest.raises(InputError):
        message_pin_v1(user1[token], invalid_mID)

#* Test that an InputError is raised when trying to pin a pinned message
def test_message_pin_pinned(user1, user2):
    channel = src.channels.channels_create_v1(user1[token], 'CJWY', True)
    m1 = message_send_v1(user1[token], channel[cID], 'We got a number one victory royale')
    message_pin_v1(user1[token], m1[mID])
    
    with pytest.raises(InputError):
        message_pin_v1(user1[token], m1[mID])

    dm = src.dm.dm_create_v1(user1[token], [user2[AuID]])
    m2 = message_senddm_v1(user1[token], dm[dmID], 'Yeah, Fortnite, we bout to get down')
    message_pin_v1(user1[token], m2[mID])

    with pytest.raises(InputError):
        message_pin_v1(user1[token], m2[mID])

#* Test that an AccessError is raised when trying to pin a message inside a channel/DM that they are not in
def test_message_pin_not_member(user1, user2, user3):
    channel = src.channels.channels_create_v1(user1[token], 'Still CJWY', True)
    m1 = message_send_v1(user1[token], channel[cID], 'Ten kills on the board right now')

    with pytest.raises(AccessError):
        message_pin_v1(user2[token], m1[mID])
    
    with pytest.raises(AccessError):
        message_pin_v1(user3[token], m1[mID])

    dm = src.dm.dm_create_v1(user1[token], [user2[AuID]])
    m2 = message_senddm_v1(user1[token], dm[dmID], 'Just wiped out Tomato Town')

    with pytest.raises(AccessError):
        message_pin_v1(user3[token], m2[mID])

#* Testing that a valid message is unpinned for channel
def test_message_unpin_valid_channel(user1):
    channel = src.channels.channels_create_v1(user1[token], 'Scissor Salad', True)
    message_send_v1(user1[token], channel[cID], 'Le from downtown')
    target = message_send_v1(user1[token], channel[cID], 'AIRBALL')
    message_pin_v1(user1[token], target[mID])
    pinned = src.channel.channel_messages_v1(user1[token], channel[cID], 0)
    
    mID_found = False
    for message in pinned['messages']:
        if target[mID] == message[mID]:
            mID_found = True
            assert message['is_pinned'] is True
        else:
            assert message['is_pinned'] is False
    assert mID_found is True
    
    message_unpin_v1(user1[token], target[mID])
    not_pinned = src.channel.channel_messages_v1(user1[token], channel[cID], 0)

    mID_found = False
    for message in not_pinned['messages']:
        if target[mID] == message[mID]:
            mID_found = True
        assert message['is_pinned'] is False
    assert mID_found is True


#* Testing that a valid message is unpinned for DM
def test_message_unpin_valid_dm(user1, user2):
    dm = src.dm.dm_create_v1(user1[token], [user2[AuID]])
    message_senddm_v1(user1[token], dm[dmID], 'Thumb it to summit')
    target = message_senddm_v1(user1[token], dm[dmID], 'Pin it to win it')
    message_pin_v1(user1[token], target[mID])
    pinned = src.dm.dm_messages_v1(user1[token], dm[dmID], 0)
    
    mID_found = False
    for message in pinned['messages']:
        if target[mID] == message[mID]:
            mID_found = True
            assert message['is_pinned'] is True
        else:
            assert message['is_pinned'] is False
    assert mID_found is True

    message_unpin_v1(user1[token], target[mID])
    not_pinned = src.dm.dm_messages_v1(user1[token], dm[dmID], 0)
    
    mID_found = False
    for message in not_pinned['messages']:
        if target[mID] == message[mID]:
            mID_found = True
        assert message['is_pinned'] is False
    assert mID_found is True
    
#* Test that an InputError is raised when the message_id is invalid
def test_message_unpin_invalid_mID(user1, user2):
    channel = src.channels.channels_create_v1(user1[token], 'telepatia', True)
    m1 = message_send_v1(user1[token], channel[cID], 'Harry Houdini')
    message_pin_v1(user1[token], m1[mID])
    message_remove_v1(user1[token], m1[mID])

    with pytest.raises(InputError):
        message_unpin_v1(user1[token], m1[mID])

    dm = src.dm.dm_create_v1(user1[token], [user2[AuID]])
    m2 = message_senddm_v1(user1[token], dm[dmID], 'He gone')
    message_pin_v1(user1[token], m2[mID])
    message_remove_v1(user1[token], m2[mID])

    with pytest.raises(InputError):
        message_unpin_v1(user1[token], m2[mID])

#* Test that an InputError is raised when trying to unpin an unpinned message
def test_message_unpin_unpinned_(user1, user2):
    channel = src.channels.channels_create_v1(user1[token], 'Vincent Le', True)
    m1 = message_send_v1(user1[token], channel[cID], 'Noted')
    
    with pytest.raises(InputError):
        message_unpin_v1(user1[token], m1[mID])

    dm = src.dm.dm_create_v1(user1[token], [user2[AuID]])
    m2 = message_senddm_v1(user1[token], dm[dmID], 'Noted')

    with pytest.raises(InputError):
        message_unpin_v1(user1[token], m2[mID])

#* Test that an AccessError is raised when trying to unpin a message inside a channel/DM that are not in
def test_message_unpin_not_member(user1, user2, user3):
    channel = src.channels.channels_create_v1(user1[token], 'Run outta', True)
    m1 = message_send_v1(user1[token], channel[cID], 'messages')
    message_pin_v1(user1[token], m1[mID])

    with pytest.raises(AccessError):
        message_unpin_v1(user2[token], m1[mID])
    
    with pytest.raises(AccessError):
        message_unpin_v1(user3[token], m1[mID])

    dm = src.dm.dm_create_v1(user1[token], [user2[AuID]])
    m2 = message_senddm_v1(user1[token], dm[dmID], 'to type')
    message_pin_v1(user1[token], m2[mID])

    with pytest.raises(AccessError):
        message_unpin_v1(user3[token], m2[mID])

#* Testing that for an invalid token, an AccessError is raised for 'pin' functions
def test_message_pin_unauthorised_user(user1, invalid_token):
    channel = src.channels.channels_create_v1(user1[token], 'Last', True)
    m1 = message_send_v1(user1[token], channel[cID], 'One')
    m2 = message_send_v1(user1[token], channel[cID], 'Bois')
    message_pin_v1(user1[token], m1[mID])
    
    with pytest.raises(AccessError):
        message_unpin_v1(invalid_token, m1[mID])
    
    with pytest.raises(AccessError):
        message_pin_v1(invalid_token, m2[mID])

#Input Error test for invalid message id for message_react
def test_message_react_v1_errors_invalid_mID(user1, user2):
    invalid_message_id = -1 
    with pytest.raises(InputError):
        message_react_v1(user1[token], invalid_message_id, thumbsUp) 

#Input error test for invalid react id for message_react 
def test_message_react_v1_errors_invalid_rID(user1, user2): 
    channel_1 = src.channels.channels_create_v1(user1[token], 'Channel', True)
    message_1 = message_send_v1(user1[token], channel_1[cID], "Hello")
    
    dm_1 = src.dm.dm_create_v1(user1[token], [user2[AuID]])
    message_2 = message_senddm_v1(user1[token], dm_1[dmID], "Goodbye")

    invalid_react_id = -1 
    #Invalid rID for channel 
    with pytest.raises(InputError):
        message_react_v1(user1[token], message_1[mID], invalid_react_id) 
      
    #Invalid rID for DM
    with pytest.raises(InputError):
        message_react_v1(user1[token], message_2[mID], invalid_react_id)

#Test that already contains an active react raises input error  
def test_message_react_v1_active_react(user1, user2):
    channel_1 = src.channels.channels_create_v1(user1[token], 'Channel', True)
    message_1 = src.message.message_send_v1(user1[token], channel_1[cID], "Hello")
    message_react_v1(user1[token], message_1[mID], thumbsUp)
    
    #Already contains react in channel error 
    with pytest.raises(InputError):
        message_react_v1(user1[token], message_1[mID], thumbsUp)
    
    dm_1 = src.dm.dm_create_v1(user1[token], [user2[AuID]])
    message_2 = message_senddm_v1(user1[token], dm_1[dmID], "Goodbye")
    message_react_v1(user1[token], message_2[mID], thumbsUp)
    
    #Already contains react in DM error
    with pytest.raises(InputError):
        message_react_v1(user1[token], message_2[mID], thumbsUp)
   
#Test that authorised user not a member of channel or dm raises access error for message_react 
def test_message_react_v1_invalid_user(user1, user2, user3): 
    channel_1 = src.channels.channels_create_v1(user1[token], 'Channel', False)
    message_1 = message_send_v1(user1[token], channel_1[cID], "Hello")
    
    #Not a member of channel 
    with pytest.raises(AccessError):
        message_react_v1(user2[token], message_1[mID], thumbsUp)
    
    dm_1 = src.dm.dm_create_v1(user1[token], [user2[AuID]])
    message_2 = message_senddm_v1(user1[token], dm_1[dmID], "Goodbye")
    
    #Not a member of DM 
    with pytest.raises(AccessError):
        message_react_v1(user3[token], message_2[mID], thumbsUp)

#Test that message_react works for a message in a channel
def test_message_react_v1_valid_channel(user1, user2):
    channel_1 = src.channels.channels_create_v1(user1[token], 'Channel', False)
    src.channel.channel_invite_v1(user1[token], channel_1[cID], user2[AuID])
    message_1 = message_send_v1(user1[token], channel_1[cID], "Hello")
    message_react_v1(user1[token], message_1[mID], thumbsUp)
    message_react_v1(user2[token], message_1[mID], thumbsUp)
    
    #Test 1: check that react_1 comes up in "messages"
    result = src.channel.channel_messages_v1(user1[token], channel_1[cID], 0)

    #Create for loop that finds message looking for 
    for current_message in result['messages']: 
        if current_message[mID] == message_1[mID]: 
            #Now that the message is found, can assert that our user has reacted to it    
            for current_react in current_message['reacts']: 
                if current_react['react_id'] == thumbsUp:
                    assert user1[AuID] in current_react['u_ids'] 
                assert current_react['is_this_user_reacted'] == True 

#Test that message_react works for a dm 
def test_message_react_v1_valid_dm(user1, user2):
    dm_1 = src.dm.dm_create_v1(user1[token], [user2[AuID]])
    message_1 = message_senddm_v1(user1[token], dm_1[dmID], "Goodbye")
    message_react_v1(user1[token], message_1[mID], thumbsUp)
    message_react_v1(user2[token], message_1[mID], thumbsUp)
    
    #Test 1: check that reacts comes up in "messages"
    result = src.dm.dm_messages_v1(user1[token], dm_1[dmID], 0)
    #Create for loop that finds message looking for 
    for current_message in result['messages']: 
        if current_message[mID] == message_1[mID]: 
            #Now that the message is found, can assert that our user has reacted to it       
            for current_react in current_message['reacts']: 
                if current_react['react_id'] == thumbsUp:
                    assert user1[AuID] in current_react['u_ids'] 
                assert current_react['is_this_user_reacted'] == True 

#Input Error test for invalid message id for message_unreact
def test_message_unreact_v1_errors_invalid_mID(user1, user2):
    invalid_message_id = -1 
    with pytest.raises(InputError):
        message_unreact_v1(user1[token], invalid_message_id, thumbsUp) 
        

#Input error test for invalid react id for message_unreact 
def test_message_unreact_v1_errors_invalid_rID(user1, user2): 
    channel_1 = src.channels.channels_create_v1(user1[token], 'Channel', True)
    message_1 = message_send_v1(user1[token], channel_1[cID], "Hello")
    
    dm_1 = src.dm.dm_create_v1(user1[token], [user2[AuID]])
    message_2 = message_senddm_v1(user1[token], dm_1[dmID], "Goodbye")

    invalid_react_id = -1 
    #Invalid rID for channel 
    with pytest.raises(InputError):
        message_unreact_v1(user1[token], message_1[mID], invalid_react_id) 
      
    #Invalid rID for DM
    with pytest.raises(InputError):
        message_unreact_v1(user1[token], message_2[mID], invalid_react_id)

#Test that doesn't contain react raises input error for message_unreact
def test_message_unreact_v1_active_react(user1, user2):
    channel_1 = src.channels.channels_create_v1(user1[token], 'Channel', True)
    message_1 = src.message.message_send_v1(user1[token], channel_1[cID], "Hello")
    
    #Doesn't contain react in channel error 
    with pytest.raises(InputError):
        message_unreact_v1(user1[token], message_1[mID], thumbsUp)
        
    
    dm_1 = src.dm.dm_create_v1(user1[token], [user2[AuID]])
    message_2 = message_senddm_v1(user1[token], dm_1[dmID], "Goodbye")
    
    #Doesn't contain react in DM error
    with pytest.raises(InputError):
        message_unreact_v1(user1[token], message_2[mID], thumbsUp)
    
#Test that authorised user not a member of channel or dm raises access error for message_react 
def test_message_unreact_v1_invalid_user(user1, user2, user3): 
    channel_1 = src.channels.channels_create_v1(user1[token], 'Channel', False)
    message_1 = message_send_v1(user1[token], channel_1[cID], "Hello")
    
    #Not a member of channel 
    with pytest.raises(AccessError):
        message_unreact_v1(user2[token], message_1[mID], thumbsUp)
    
    dm_1 = src.dm.dm_create_v1(user1[token], [user2[AuID]])
    message_2 = message_senddm_v1(user1[token], dm_1[dmID], "Goodbye")
    
    #Not a member of DM 
    with pytest.raises(AccessError):
        message_unreact_v1(user3[token], message_2[mID], thumbsUp)

#Test that message_unreact works for a message in a channel
def test_message_unreact_v1_valid_channel(user1, user2):
    channel_1 = src.channels.channels_create_v1(user1[token], 'Channel', False)
    src.channel.channel_invite_v1(user1[token], channel_1[cID], user2[AuID])
    message_1 = message_send_v1(user1[token], channel_1[cID], "Hello")
    message_react_v1(user1[token], message_1[mID], thumbsUp)
    message_unreact_v1(user1[token], message_1[mID], thumbsUp)
    
    #Test 1: check that react_1 no longer comes up in "messages"
    result = src.channel.channel_messages_v1(user1[token], channel_1[cID], 0)
    
    #Create for loop that finds message looking for 
    for current_message in result['messages']: 
        if current_message[mID] == message_1[mID]: 
            #Now that the message is found, can assert that our user has reacted to it  
            for current_react in current_message['reacts']: 
                if current_react['react_id'] == thumbsUp:
                    assert user1[AuID] not in current_react['u_ids']
                assert current_react['is_this_user_reacted'] == False 
                
#Test that message_unreact works for a dm 
def test_message_unreact_v1_valid_dm(user1, user2):
    dm_1 = src.dm.dm_create_v1(user1[token], [user2[AuID]])
    message_1 = message_senddm_v1(user1[token], dm_1[dmID], "Goodbye")
    message_react_v1(user1[token], message_1[mID], thumbsUp)
    message_unreact_v1(user1[token], message_1[mID], thumbsUp)
    
    #Test 1: check that react no longer comes up in "messages"
    result = src.dm.dm_messages_v1(user1[token], dm_1[dmID], 0)
    #Create for loop that finds message looking for 
    for current_message in result['messages']: 
        if current_message[mID] == message_1[mID]: 
            #Now that the message is found, can assert that our user has reacted to it       
            for current_react in current_message['reacts']: 
                if current_react['react_id'] == thumbsUp:
                    assert user1[AuID] not in current_react['u_ids'] 
                assert current_react['is_this_user_reacted'] == False
#* Testing a message that is to be sent later isn't prematurely sent
def test_message_sendlater_is_sent_later(user1, user2):
    # User1 creates channel
    channel1 = src.channels.channels_create_v1(user1[token], 'Dominic Torreto', True)
    # User2 joins channel
    src.channel.channel_join_v1(user2[token], channel1[cID])
    # Test for m1, sent by user1
    sendTime = datetime.now().replace(tzinfo=timezone.utc).timestamp() + 3
    m1 = src.message.message_sendlater_v1(user1[token], channel1[cID], "You know what matters more than American Muscle?", sendTime)

    #* Make sure message isn't sent prematurely
    messageFound = False
    for message in src.channel.channel_messages_v1(user2[token], channel1[cID], 0)['messages']:
        if m1[mID] == message[mID]:
            messageFound = True
    assert not messageFound

    #* Sleep for now
    time.sleep(4)
    
    #* Make sure the message is sent and the timestamp is correct
    for message in src.channel.channel_messages_v1(user2[token], channel1[cID], 0)['messages']:
        if m1[mID] == message[mID]:
            mTime = message['time_created']
            messageFound = True
    assert messageFound
    assert mTime == sendTime


#* Testing a message that is to be sent later isn't prematurely sent
def test_message_sendlaterdm_is_sent_later(user1, user2):
    # User1 creates dm, invites user2
    dm1 = src.dm.dm_create_v1(user1[token], [user2[AuID]])
    # Test for m1, sent by user1
    sendTime = datetime.now().replace(tzinfo=timezone.utc).timestamp() + 3
    m1 = src.message.message_sendlaterdm_v1(user1[token], dm1[dmID], "You know what matters more than American Muscle?", sendTime)
    
    #* Make sure message isn't sent prematurely
    messageFound = False
    for message in src.dm.dm_messages_v1(user2[token], dm1[dmID], 0)['messages']:
        if m1[mID] == message[mID]:
            messageFound = True
    assert not messageFound

    #* Sleep for now
    time.sleep(4)
    
    #* Make sure the message is sent and the timestamp is correct
    for message in src.dm.dm_messages_v1(user2[token], dm1[dmID], 0)['messages']:
        if m1[mID] == message[mID]:
            mTime = message['time_created']
            messageFound = True
    assert messageFound
    assert mTime == sendTime

#* Testing a message that is to be sent later isn't too long
def test_message_sendlater_long_messages(user1, user2):
    # User1 creates channel
    channel1 = src.channels.channels_create_v1(user1[token], 'Dominic Torreto', True)
    # User2 joins channel
    src.channel.channel_join_v1(user2[token], channel1[cID])
    # Test for m1, sent by user1
    sendTime = datetime.now().replace(tzinfo=timezone.utc).timestamp() + 3
    tooLong = ""
    for _ in range(501):
        tooLong += ":("
    with pytest.raises(InputError):
        src.message.message_sendlater_v1(user1[token], channel1[cID], tooLong, sendTime)

#* Testing a message that is to be sent later isn't too long
def test_message_sendlaterdm_long_messages(user1, user2):
    # User1 creates dm, invites user2
    dm1 = src.dm.dm_create_v1(user1[token], [user2[AuID]])
    # Test for m1, sent by user1
    sendTime = datetime.now().replace(tzinfo=timezone.utc).timestamp() + 3
    tooLong = ""
    for _ in range(501):
        tooLong += ":("
    with pytest.raises(InputError):
        src.message.message_sendlaterdm_v1(user1[token], dm1[dmID], tooLong, sendTime)

def test_message_sendlater_other_user(user1, user2, user3):
    # User1 creates channel
    channel1 = src.channels.channels_create_v1(user1[token], 'Dominic Torreto', True)
    # User2 joins channel
    src.channel.channel_join_v1(user2[token], channel1[cID])
    # Test for m1, sent by user3
    sendTime = datetime.now().replace(tzinfo=timezone.utc).timestamp() + 3
    messageToSend = "Quack"
    with pytest.raises(AccessError):
        src.message.message_sendlater_v1(user3[token], channel1[cID], messageToSend, sendTime)

def test_message_sendlaterdm_other_user(user1, user2, user3):
    # User1 creates dm, invites user2
    dm1 = src.dm.dm_create_v1(user1[token], [user2[AuID]])
    # Test for m1, sent by user3
    sendTime = datetime.now().replace(tzinfo=timezone.utc).timestamp() + 3
    messageToSend = "Quack quack"
    with pytest.raises(AccessError):
        src.message.message_sendlaterdm_v1(user3[token], dm1[dmID], messageToSend, sendTime)

def test_message_sendlater_past(user1, user2, user3):
    # User1 creates channel
    channel1 = src.channels.channels_create_v1(user1[token], 'Dominic Torreto', True)
    # User2 joins channel
    src.channel.channel_join_v1(user2[token], channel1[cID])
    # Test for m1, sent by user3
    sendTime = datetime.now().replace(tzinfo=timezone.utc).timestamp() - 5
    messageToSend = "Quack"
    with pytest.raises(InputError):
        src.message.message_sendlater_v1(user3[token], channel1[cID], messageToSend, sendTime)

def test_message_sendlaterdm_past(user1, user2, user3):
    # User1 creates dm, invites user2
    dm1 = src.dm.dm_create_v1(user1[token], [user2[AuID]])
    # Test for m1, sent by user3
    sendTime = datetime.now().replace(tzinfo=timezone.utc).timestamp() - 5
    messageToSend = "Quack quack"
    with pytest.raises(InputError):
        src.message.message_sendlaterdm_v1(user3[token], dm1[dmID], messageToSend, sendTime)
