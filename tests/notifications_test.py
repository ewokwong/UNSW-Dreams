import pytest
from src.message import message_send_v1, message_remove_v1, message_edit_v1, message_share_v1, message_senddm_v1, message_react_v1
from src.error import InputError, AccessError
import src.channel, src.channels, src.auth
from src.other import get_user, get_channel, get_dm, clear_v1, SECRET
from datetime import timezone, datetime
from src.notifications import notifications_get_v1
import jwt
from src.dm import dm_create_v1, dm_invite_v1

AuID   = 'auth_user_id'
cID    = 'channel_id'
token  = 'token'
nMess  = 'notification_message'
notifs = 'notifications'
AuID = 'auth_user_id'
dmID = 'dm_id'
handle = 'handle_str'
mID = 'message_id'
thumbsUp = 1

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

def test_notifications_get_in_channels(user1, user2, user3):
    # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #   Note: This test has white-box testing involved  #
    # # # # # # # # # # # # # # # # # # # # # # # # # # #

    channel1 = src.channels.channels_create_v1(user1[token], 'TrumpPence', True)

    #* Test 1: Test if added into channel notif comes up
    src.channel.channel_invite_v1(user1[token], channel1[cID], user2[AuID])
    assert {
        cID    : channel1[cID],
        'dm_id': -1,
        nMess  : f"{get_user(user1[AuID])['handle_str']} added you to {get_channel(channel1[cID])['name']}",
    } in notifications_get_v1(user2[token])[notifs]
    src.channel.channel_invite_v1(user1[token], channel1[cID], user3[AuID])
    assert {
        cID    : channel1[cID],
        'dm_id': -1,
        nMess  : f"{get_user(user1[AuID])['handle_str']} added you to {get_channel(channel1[cID])['name']}",
    } in notifications_get_v1(user3[token])[notifs]

    #* Test 2: Test if mentions and preview notif comes up
    message_send_v1(user2[token], channel1[cID], f"Hello @{get_user(user1[AuID])['handle_str']} @{get_user(user3[AuID])['handle_str']}")
    assert {
        cID    : channel1[cID],
        'dm_id': -1,
        nMess  : f"{get_user(user2[AuID])['handle_str']} tagged you in {get_channel(channel1[cID])['name']}: Hello @{get_user(user1[AuID])['handle_str']} @{get_user(user3[AuID])['handle_str']}",
    } in notifications_get_v1(user1[token])[notifs]
    assert {
        cID    : channel1[cID],
        'dm_id': -1,
        nMess  : f"{get_user(user2[AuID])['handle_str']} tagged you in {get_channel(channel1[cID])['name']}: Hello @{get_user(user1[AuID])['handle_str']} @{get_user(user3[AuID])['handle_str']}",
    } in notifications_get_v1(user3[token])[notifs]
    assert {
        cID    : channel1[cID],
        'dm_id': -1,
        nMess  : f"{get_user(user1[AuID])['handle_str']} added you to {get_channel(channel1[cID])['name']}",
    } in notifications_get_v1(user3[token])[notifs]

    #* Test 3: Only recent 20 notifs come up
    i = 0
    while i < 22:
        message_send_v1(user1[token], channel1[cID], f"Hi @{get_user(user2[AuID])['handle_str']} @{get_user(user3[AuID])['handle_str']}")
        i += 1
    assert {
        cID    : channel1[cID],
        'dm_id': -1,
        nMess  : f"{get_user(user1[AuID])['handle_str']} added you to {get_channel(channel1[cID])['name']}",
    } not in notifications_get_v1(user3[token])[notifs]
    assert {
        cID    : channel1[cID],
        'dm_id': -1,
        nMess  : f"{get_user(user2[AuID])['handle_str']} tagged you in {get_channel(channel1[cID])['name']}: Hello @{get_user(user1[AuID])['handle_str']} @{get_user(user3[AuID])['handle_str']}",
    } not in notifications_get_v1(user3[token])[notifs]

    i = 0
    while i < 21:
        if i == 0:
            message_send_v1(user3[token], channel1[cID], f"Baby shark @{get_user(user2[AuID])['handle_str']}")
        else:
            message_send_v1(user3[token], channel1[cID], f"Dooo dooo dooo dooo @{get_user(user2[AuID])['handle_str']}")
        i += 1
    assert {
        cID    : channel1[cID],
        'dm_id': -1,
        nMess  : f"{get_user(user3[AuID])['handle_str']} tagged you in {get_channel(channel1[cID])['name']}: Baby shark @{get_user(user2[AuID])['handle_str']}",
    } not in notifications_get_v1(user2[token])[notifs]

    #* Test 4: Only first 20 characters
    assert {
        cID    : channel1[cID],
        'dm_id': -1,
        nMess  : f"{get_user(user3[AuID])['handle_str']} tagged you in {get_channel(channel1[cID])['name']}: Dooo dooo dooo dooo ",
    } in notifications_get_v1(user2[token])[notifs]
    
    #* Test if @ without a valid handle string won't raise an error nor tag anyone
    src.message.message_send_v1(user1[token], channel1[cID], "@Joe_Biden")
    assert {
        cID    : channel1[cID],
        'dm_id': -1,
        nMess  : f"{get_user(user1[AuID])['handle_str']} tagged you in {get_channel(channel1[cID])['name']}: @Joe_Biden",
    } not in notifications_get_v1(user2[token])[notifs]
    assert {
        cID    : channel1[cID],
        'dm_id': -1,
        nMess  : f"{get_user(user1[AuID])['handle_str']} tagged you in {get_channel(channel1[cID])['name']}: @Joe_Biden",
    } not in notifications_get_v1(user3[token])[notifs]
    

def test_notifications_dms_added(user1, user2, user3):
    #Test that a notif is sent to user when they are added to dm with channel id = -1
    #Ordered from most to least recent
    dm_0 = dm_create_v1(user1[token], [user2[AuID]])
    dm_1 = dm_create_v1(user1[token], [user3[AuID]])

    #Test 1: for initial creation of DM
    assert {
        cID : -1,
        'dm_id': 0,
        nMess : f"{get_user(user1[AuID])['handle_str']} added you to {get_dm(dm_0['dm_id'])['name']}",
    } in notifications_get_v1(user2[token])[notifs]

    #Test 2: For DM_invite inviting another person
    dm_invite_v1(user1[token], dm_0['dm_id'], user3[AuID])

    assert {
        cID : -1,
        'dm_id': 0,
        nMess : f"{get_user(user1[AuID])['handle_str']} added you to {get_dm(dm_0['dm_id'])['name']}",
    } in notifications_get_v1(user3[token])[notifs]

    #Test 3: if being added to another dm the old dm is still there 
    assert {
        cID : -1,
        'dm_id': 1,
        nMess : f"{get_user(user1[AuID])['handle_str']} added you to {get_dm(dm_1['dm_id'])['name']}",
    } in notifications_get_v1(user3[token])[notifs]

#* When tagged, correct amount of tags come up
def test_valid_dm_tag(user1, user2):
    dm1= dm_create_v1(user1[token], [user2[AuID]])
    message_senddm_v1(user1[token], dm1[dmID], f"Hi @{get_user(user2[AuID])[handle]}")
    message_senddm_v1(user2[token], dm1[dmID], f"Hi @{get_user(user1[AuID])[handle]}")
    assert len(notifications_get_v1(user1[token])[notifs]) == 1
    assert len(notifications_get_v1(user2[token])[notifs]) == 2

#* Only first 20 characters of the message come up
def test_valid_dm_20_chars(user1, user2):
    dm1= dm_create_v1(user1[token], [user2[AuID]])
    tagMessage = f"@{get_user(user2[AuID])[handle]}"
    message = tagMessage + ' ' + f"{'a'*25}"
    message_senddm_v1(user1[token], dm1[dmID], message)

    assert {
        cID : -1,
        dmID: dm1[dmID],
        nMess : f"{get_user(user1[AuID])['handle_str']} tagged you in {get_dm(dm1['dm_id'])['name']}: {message[0:20]}",
    } in notifications_get_v1(user2[token])[notifs]

#* Test that users that are not in the DM cannot be tagged
def test_dm_no_tag(user1, user2, user3):
    dm1= dm_create_v1(user1[token], [user2[AuID]])
    message_senddm_v1(user1[token], dm1[dmID], f"Hi @{get_user(user3[AuID])[handle]}")
    assert notifications_get_v1(user3[token])[notifs] == []

#* When tagged >20 times, only 20 tags come up (and oldest ones dont show up)
def test_dm_20_notifs(user1, user2):
    dm1= dm_create_v1(user1[token], [user2[AuID]])
    tagMessage = f"@{get_user(user2[AuID])[handle]}"
    for nNum in range(21):
        message = str(nNum) + ' ' + tagMessage
        message_senddm_v1(user1[token], dm1[dmID], message)
    assert len(notifications_get_v1(user2[token])[notifs]) == 20
    assert {
        cID : -1,
        dmID: dm1[dmID],
        nMess : f"{get_user(user1[AuID])['handle_str']} tagged you in {get_dm(dm1['dm_id'])['name']}: 0 {tagMessage}",
    } not in notifications_get_v1(user2[token])[notifs]

#* Test message edit sends a new notif in dms
def test_dm_edit_notif(user1, user2):
    dm1 = dm_create_v1(user1[token], [user2[AuID]])
    tagMessage = f"@{get_user(user2[AuID])[handle]}"
    dmMessage = message_senddm_v1(user1[token], dm1[dmID], tagMessage)
    message_edit_v1(user1[token], dmMessage['message_id'], f"Yo @{get_user(user2[AuID])[handle]}")
    assert {
        cID : -1,
        dmID: dm1[dmID],
        nMess : f"{get_user(user1[AuID])['handle_str']} tagged you in {get_dm(dm1['dm_id'])['name']}: {tagMessage}",
    } in notifications_get_v1(user2[token])[notifs]
    assert {
        cID : -1,
        dmID: dm1[dmID],
        nMess : f"{get_user(user1[AuID])['handle_str']} tagged you in {get_dm(dm1['dm_id'])['name']}: Yo {tagMessage}",
    } in notifications_get_v1(user2[token])[notifs]
    
#Test that notification is received when there is a react to a message in a channel 
def test_react_notif_in_channel(user1, user2):
    channel1 = src.channels.channels_create_v1(user1[token], 'Hello', True)
    src.channel.channel_invite_v1(user1[token], channel1[cID], user2[AuID])
    message1 =  message_send_v1(user1[token], channel1[cID], "Good-bye")
    message_react_v1(user2[token], message1[mID], thumbsUp)
    
    assert {
        cID: channel1[cID],
        dmID: -1, 
        nMess: f"{get_user(user2[AuID])['handle_str']} reacted to your message in {get_channel(channel1['channel_id'])['name']}"
    } in notifications_get_v1(user1[token])[notifs]
    
    
'''
#Test that notification is received when there is a react to a message in a dm
def test_react_notif_in_dm(user1, user2):
    dm1 = dm_create_v1(user1[token], [user2[AuID]])
    message1 =  message_senddm_v1(user1[token], dm1[dmID], "Hello")
    message_react_v1(user2[token], message1[mID], thumbsUp)
    
    assert {
        cID: -1,
        dmID: dm1[dmID],
        nMess: f"{get_user(user2[AuID])['handle_str']} reacted to your message in {get_dm(dm1['dm_id'])['name']}",
    } in notifications_get_v1(user1[token])[notifs]
'''

