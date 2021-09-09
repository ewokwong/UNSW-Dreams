import pytest
import src.channel, src.channels, src.message, src.dm
import jwt
from src.other import clear_v1, search_v1, get_channel, get_user, get_message
from src.error import AccessError, InputError

AuID   = 'auth_user_id'
cID    = 'channel_id'
mID    = 'message_id'
uID    = 'u_id'
token  = 'token'

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

@pytest.fixture
def channel1(user1):
    return src.channels.channels_create_v1(user1[token], 'TrumpPence', True)

@pytest.fixture
def channel2(user2):
    return src.channels.channels_create_v1(user2[token], 'BidenHarris', False)

# search_v1
# When query_str is >1000 characters, InputError is raised
# Test that users can only see messages in channels that they have joined
    # Test if a user who has joined no channels can see any messages
def test_search_channels(user1, user2, user3, user4, user5, channel1, channel2):
    # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #   Note: This test has white-box testing involved  #
    # # # # # # # # # # # # # # # # # # # # # # # # # # #

    #* Test if a user who has joined no channels can see any messages
    assert search_v1(user5[token], "om")['messages'] == []

    #* user3 will join channel1, user4 will be invited into channel2, user5 will be invited into both
    src.channel.channel_join_v1(user3[token], channel1[cID])
    src.channel.channel_invite_v1(user2[token], channel2[cID], user4[AuID])
    src.channel.channel_invite_v1(user1[token], channel1[cID], user5[AuID])
    src.channel.channel_invite_v1(user2[token], channel2[cID], user5[AuID])

    #* users 1, 2, 3 & 4 will send a bunch of messages containing "om"
    message1 = src.message.message_send_v1(user1[token], channel1[cID], "Welcome")
    message2 = src.message.message_send_v1(user2[token], channel2[cID], "Akeome")
    message3 = src.message.message_send_v1(user3[token], channel1[cID], "omg")
    message4 = src.message.message_send_v1(user4[token], channel2[cID], "Nomnom")

    #* user3 will send a message without "om"
    message5 = src.message.message_send_v1(user3[token], channel1[cID], "Bruh haha")

    #* Check if messages 1 to 4 comes up for user5's search
    assert {
        mID: message1[mID],
        uID: user1[AuID],
        'message': "Welcome",
        'time_created': get_message(message1[mID])['time_created'],
    } in search_v1(user5[token], "om")['messages']
    assert {
        mID: message2[mID],
        uID: user2[AuID],
        'message': "Akeome",
        'time_created': get_message(message2[mID])['time_created'],
    } in search_v1(user5[token], "om")['messages']
    assert {
        mID: message3[mID],
        uID: user3[AuID],
        'message': "omg",
        'time_created': get_message(message3[mID])['time_created'],
    } in search_v1(user5[token], "om")['messages']
    assert {
        mID: message4[mID],
        uID: user4[AuID],
        'message': "Nomnom",
        'time_created': get_message(message4[mID])['time_created'],
    } in search_v1(user5[token], "om")['messages']

    #* Check if message 5 does not come up for user5's search
    assert {
        mID: message5[mID],
        uID: user5[AuID],
        'message': "Bruh haha",
        'time_created': get_message(message5[mID])['time_created'],
    } not in search_v1(user5[token], "om")['messages']

    #* Test if InputError is raised when query_str is >1000
    tooLongMessage = ""
    for _ in range(1002):
        tooLongMessage += "@"
    with pytest.raises(InputError):
        search_v1(user5[token], tooLongMessage)

    #* Test if a user can't view messages from channels it isn't in
    assert {
        mID: message3[mID],
        uID: user3[AuID],
        'message': "omg",
        'time_created': get_message(message5[mID])['time_created'],
    } not in search_v1(user2[token], "om")['messages']

    #* Test if the search is not case sentitive
    message6 = src.message.message_send_v1(user4[token], channel2[cID], "Joe Biden")
    assert {
        mID: message6[mID],
        uID: user4[AuID],
        'message': "Joe Biden",
        'time_created': get_message(message6[mID])['time_created'],
    } in search_v1(user2[token], "jOE bIDEN")['messages']

    #* Finished testing for this function
    #! Clearing data
    clear_v1()

def test_search_dms(user1, user2, user3):
    # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #   Note: This test has white-box testing involved  #
    # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Create dm
    dm1 = src.dm.dm_create_v1(user1[token], [user2[AuID]])
    #* Test if search comes up in dms for user2 (who is in dm)
    dmMessage = src.message.message_senddm_v1(user1[token], dm1['dm_id'], "Biden Harris 2020")
    assert {
        mID: dmMessage[mID],
        uID: user1[AuID],
        'message': "Biden Harris 2020",
        'time_created': get_message(dmMessage[mID])['time_created'],
    } in search_v1(user2[token], "bIDEN h")['messages']
    #* Test if search doesn't comes up in dms for user3 (who is not in dm)
    assert {
        mID: dmMessage[mID],
        uID: user1[AuID],
        'message': "Biden Harris 2020",
        'time_created': get_message(dmMessage[mID])['time_created'],
    } not in search_v1(user3[token], "bIDEN h")['messages']
