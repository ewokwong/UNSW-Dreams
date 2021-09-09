from src.error import AccessError, InputError
import pytest
from src.user import user_profile_v2, user_setname_v2, user_setemail_v2, user_sethandle_v2, users_all, users_stats_v1, user_stats_v1,user_profile_uploadphoto_v1
from src.auth import auth_register_v2, auth_login_v2
from src.other import clear_v1, SECRET
from src.channel import channel_join_v1
from src.channels import channels_create_v1
from src.dm import dm_create_v1, dm_invite_v1
from src.message import message_send_v1, message_remove_v1, message_senddm_v1
import jwt
from PIL import Image
from src.config import url

AuID    = 'auth_user_id'
uID     = 'u_id'
cID     = 'channel_id'
chans   = 'channels'
allMems = 'all_members'
ownMems = 'owner_members'
fName   = 'name_first'
lName   = 'name_last'
tok   = 'token'
mID     = 'message_id'
dmID    = 'dm_id'
Name    = 'name'

@pytest.fixture
def invalid_token():
    return jwt.encode({'session_id': -1, 'user_id': -1}, SECRET, algorithm='HS256')

@pytest.fixture
def user1():
    clear_v1()    
    return auth_register_v2("caricoleman@gmail.com", "1234567", "cari", "coleman")

@pytest.fixture
def user2():
    return auth_register_v2("ericamondy@gmail.com", "1234567", "erica", "mondy")

@pytest.fixture
def user3():
    return auth_register_v2("hilarybently@gmail.com", "1234567", "hillary", "bently") 

@pytest.fixture
def user4():
    return auth_register_v2("kentonwatkins@gmail.com", "1234567", "kenton", "watkins") 

@pytest.fixture
def user5():
    return auth_register_v2("claudiamarley@gmail.com", "1234567", "claudia", "marley")



def test_user_profile_errors(user1):

    with pytest.raises(InputError):
        user_profile_uploadphoto_v1(user1[tok],"https://i.pinimg.com/originals/05/1b/7d/051b7d93394fc94c082f1801bc4ccfb2.jpg", -1 ,-1 ,500,500)
    with pytest.raises(InputError):
        user_profile_uploadphoto_v1(user1[tok],"https://i.pinimg.com/originals/05/1b/7d/051b7d93394fc94c082f1801bc4ccfb2.jpg", 500 ,500 ,0,0)
    with pytest.raises(InputError):    
        user_profile_uploadphoto_v1(user1[tok],"https://i.pinimg.com/originals/05/1b/7d/051b7d93394fc94c082f1801bc4ccfb2.jpg", 0 ,0 ,1000,1000)
    with pytest.raises(InputError):
        user_profile_uploadphoto_v1(user1[tok],"http://agsgasg.com/nicklam/04/2/hiiiii.jpg", 0 ,0 ,500,500)
    with pytest.raises(InputError):
        user_profile_uploadphoto_v1(user1[tok],"https://www.clipartmax.com/png/middle/450-4500720_tom-and-jerry-aesthetic.png", 0 ,0 ,500,500)


def test_user_profile_default(user1):

    userprof = user_profile_v2(user1[tok], user1[AuID])
    assert userprof == {
        'user':
        {
        'u_id': user1[AuID],
        'email': "caricoleman@gmail.com", 
        'name_first': 'cari', 
        'name_last': 'coleman', 
        'handle_str': 'caricoleman',
        'profile_img_url': f"{url}static/default.jpg",
        }
    }

def test_user_profile_change(user1,user2):

    user_profile_uploadphoto_v1(user1[tok],"https://i.pinimg.com/originals/05/1b/7d/051b7d93394fc94c082f1801bc4ccfb2.jpg", 0 ,0 ,500,500)
    
    userprof = user_profile_v2(user1[tok], user1[AuID])
    assert userprof == {
        'user':
        {
        'u_id': user1[AuID],
        'email': "caricoleman@gmail.com", 
        'name_first': 'cari', 
        'name_last': 'coleman', 
        'handle_str': 'caricoleman',
        'profile_img_url': f"{url}static/{user1[AuID]}.jpg"
        }
    }
# tests the return value when user profile is called from a valid user 
def test_user_profile_valid(user1,user2):
    user_data_1 = auth_login_v2("caricoleman@gmail.com", "1234567") 

    assert user_profile_v2(user_data_1['token'], user_data_1['auth_user_id']) == { 
        'user':
            {
            'u_id': user_data_1['auth_user_id'],
            'email': "caricoleman@gmail.com", 
            'name_first': 'cari', 
            'name_last': 'coleman', 
            'handle_str': 'caricoleman',
            'profile_img_url': f"{url}static/default.jpg"
            }
    }

# tests the return value when user profile is called from a valid user by multiple users
def test_user_profile_valid_multiple(user1,user2):

    user_data_1 = auth_login_v2("caricoleman@gmail.com", "1234567")

    user_data_2 = auth_login_v2("ericamondy@gmail.com", "1234567")

    assert user_profile_v2(user_data_1['token'], user_data_1['auth_user_id']) == { 
        'user':
            {
            'u_id': user_data_1['auth_user_id'], 
            'email': "caricoleman@gmail.com", 
            'name_first': 'cari', 
            'name_last': 'coleman', 
            'handle_str': 'caricoleman',
            'profile_img_url': f"{url}static/default.jpg"
            }
    }

    assert user_profile_v2(user_data_2['token'], user_data_2['auth_user_id']) == { 
        'user':
            {
            'u_id': user_data_2['auth_user_id'], 
            'email': "ericamondy@gmail.com", 
            'name_first': 'erica', 
            'name_last': 'mondy', 
            'handle_str': 'ericamondy',
            'profile_img_url': f"{url}static/default.jpg"
            }
    }
    

# tests the case when the provided token contains an invalid user id
def test_user_profile_invalid_user_id(user1):
    with pytest.raises(InputError):
        user_data_1 = auth_login_v2("caricoleman@gmail.com", "1234567") 
        user_profile_v2(user_data_1['token'], 1)

# tests that set name changes the users first and last names to the inputted first and last names
# where only the first name is being changed
def test_user_setname_valid_first_name(user1):
    user_data_1 = auth_login_v2("caricoleman@gmail.com", "1234567")

    assert user_setname_v2(user_data_1['token'], 'kari', 'coleman') == {}

    assert user_profile_v2(user_data_1['token'], user_data_1['auth_user_id']) == { 
        'user':
            {
            'u_id': user_data_1['auth_user_id'], 
            'email': "caricoleman@gmail.com", 
            'name_first': 'kari', 
            'name_last': 'coleman', 
            'handle_str': 'caricoleman',
            'profile_img_url': f"{url}static/default.jpg"
            }
    }

# tests that set name changes the users first and last names to the inputted first and last names 
# where only the last name is being changed
def test_user_setname_valid_last_name(user1):
    user_data_1 = auth_login_v2("caricoleman@gmail.com", "1234567")

    assert user_setname_v2(user_data_1['token'], 'cari', 'koleman') == {}

    assert  user_profile_v2(user_data_1['token'], user_data_1['auth_user_id']) == { 
        'user':
            {
            'u_id': user_data_1['auth_user_id'], 
            'email': "caricoleman@gmail.com", 
            'name_first': 'cari', 
            'name_last': 'koleman', 
            'handle_str': 'caricoleman',
            'profile_img_url': f"{url}static/default.jpg"
            }
    }

# tests that set name changes the users first and last names to the inputted first and last names 
# where both the first and last names are being changed
def test_user_setname_valid_both_names(user1):
    user_data_1 = auth_login_v2("caricoleman@gmail.com", "1234567") 

    assert user_setname_v2(user_data_1['token'], 'kari', 'koleman') == {}

    assert  user_profile_v2(user_data_1['token'], user_data_1['auth_user_id']) == { 
        'user':
            {
            'u_id': user_data_1['auth_user_id'], 
            'email': "caricoleman@gmail.com", 
            'name_first': 'kari', 
            'name_last': 'koleman', 
            'handle_str': 'caricoleman',
            'profile_img_url': f"{url}static/default.jpg"
            }
    }

# tests that set name changes the users first and last names to the inputted first and last names 
# where both the first and last names are being changed
# for multiple users
def test_user_setname_valid_multiple(user1,user2):
    user_data_1 = auth_login_v2("caricoleman@gmail.com", "1234567")
 
    user_data_2 = auth_login_v2("ericamondy@gmail.com", "1234567")

    assert user_setname_v2(user_data_1['token'], 'kari', 'koleman') == {}

    assert  user_profile_v2(user_data_1['token'], user_data_1['auth_user_id']) == {
        'user':
        {
        'u_id': user_data_1['auth_user_id'], 
        'email': "caricoleman@gmail.com", 
        'name_first': 'kari', 
        'name_last': 'koleman', 
        'handle_str': 'caricoleman',
        'profile_img_url': f"{url}static/default.jpg"
        }
    }
    
    assert user_setname_v2(user_data_2['token'], 'erika', 'money') == {}

    assert user_profile_v2(user_data_2['token'], user_data_2['auth_user_id']) == {
        'user':
        {
        'u_id': user_data_2['auth_user_id'], 
        'email': "ericamondy@gmail.com", 
        'name_first': 'erika', 
        'name_last': 'money', 
        'handle_str': 'ericamondy',
        'profile_img_url': f"{url}static/default.jpg"
        }
    }

# tests for the case where the inputted first name exceeds the 50 character limit
def test_user_setname_invalid_long_first_name(user1):
    with pytest.raises(InputError):
        user_data_1 = auth_login_v2("caricoleman@gmail.com", "1234567")

        user_setname_v2(user_data_1['token'], 'kariiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii', 'koleman') 

# tests for the case where the inputted first name is empty
def test_user_setname_invalid_no_first_name(user1):
    with pytest.raises(InputError):
        user_data_1 = auth_login_v2("caricoleman@gmail.com", "1234567") 

        user_setname_v2(user_data_1['token'], '', 'koleman') 

# tests for the case where the inputted last name exceeds the 50 character limit
def test_user_setname_invalid_long_last_name(user1):
    with pytest.raises(InputError):
        user_data_1 = auth_login_v2("caricoleman@gmail.com", "1234567")
        user_setname_v2(user_data_1['token'], 'kari', 'kolemaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaan')           

# tests for the case where the inputted last name is empty
def test_user_setname_invalid_no_last_name(user1):
    with pytest.raises(InputError):
        user_data_1 = auth_login_v2("caricoleman@gmail.com", "1234567")
        user_setname_v2(user_data_1['token'], 'kari', '') 

# tests that set email changes the users email to the inputted email
def test_user_setemail_valid(user1):
    user_data_1 = auth_login_v2("caricoleman@gmail.com", "1234567") 

    assert user_setemail_v2(user_data_1['token'], 'karicoleman@gmail.com') == {}

    assert user_profile_v2(user_data_1['token'], 0) == {
        'user':
        {
        'u_id': user_data_1['auth_user_id'], 
        'email': "karicoleman@gmail.com", 
        'name_first': 'cari', 
        'name_last': 'coleman', 
        'handle_str': 'caricoleman',
        'profile_img_url': f"{url}static/default.jpg"
        }
    }

# tests that set email changes the users email to the inputted email for multiple users
def test_user_setemail_valid_multiple(user1,user2):
    user_data_1 = auth_login_v2("caricoleman@gmail.com", "1234567")

    user_data_2 = auth_login_v2("ericamondy@gmail.com", "1234567") 

    assert user_setemail_v2(user_data_1['token'], 'karicoleman@gmail.com') == {}

    assert  user_profile_v2(user_data_1['token'], 0) == {
        'user':
        {
        'u_id': user_data_1['auth_user_id'], 
        'email': "karicoleman@gmail.com", 
        'name_first': 'cari', 
        'name_last': 'coleman', 
        'handle_str': 'caricoleman',
        'profile_img_url': f"{url}static/default.jpg"
        }
    }
    
    assert user_setemail_v2(user_data_2['token'], 'erikamoney@gmail.com') == {}

    assert  user_profile_v2(user_data_2['token'], user_data_2['auth_user_id']) == {
        'user':
        {
        'u_id': user_data_2['auth_user_id'], 
        'email': "erikamoney@gmail.com", 
        'name_first': 'erica', 
        'name_last': 'mondy', 
        'handle_str': 'ericamondy',
        'profile_img_url': f"{url}static/default.jpg"
        }
    }

# tests the case where the inputted email is of invalid format
def test_user_setemail_invalid_email(user1):
    with pytest.raises(InputError):
        user_data_1 = auth_login_v2("caricoleman@gmail.com", "1234567") 

        user_setemail_v2(user_data_1['token'], 'karicoleman.com')

# tests the case where the inputted email is already being used by another registerd user
def test_user_setemail_invalid_email_in_use(user1,user2):
    with pytest.raises(InputError):
        user_data_1 = auth_login_v2("caricoleman@gmail.com", "1234567")

        user_data_2 = auth_login_v2("ericamondy@gmail.com", "1234567") 


        assert user_setemail_v2(user_data_1['token'], 'karicoleman@gmail.com') == {}

        assert  user_profile_v2(user_data_1['token'], user_data_1['auth_user_id']) == {
            'user':
            {
            'u_id': user_data_1['auth_user_id'], 
            'email': "karicoleman@gmail.com", 
            'name_first': 'cari', 
            'name_last': 'coleman', 
            'handle_str': 'caricoleman',
            'profile_img_url': f"{url}static/default.jpg"
            }
        }
        
        user_setemail_v2(user_data_2['token'], 'karicoleman@gmail.com') 

# tests that set handle changes the users handle string to the inputted handle string
def test_user_sethandle_valid(user1):
    user_data_1 = auth_login_v2("caricoleman@gmail.com", "1234567") 

    assert user_sethandle_v2(user_data_1['token'], 'karikoleman') == {}

    assert user_profile_v2(user_data_1['token'], user_data_1['auth_user_id']) == {
        'user':
        {
        'u_id': user_data_1['auth_user_id'], 
        'email': "caricoleman@gmail.com", 
        'name_first': 'cari', 
        'name_last': 'coleman', 
        'handle_str': 'karikoleman',
        'profile_img_url': f"{url}static/default.jpg"
        }
    }

# tests that set handle changes the users handle string to the inputted handle string for multiple users
def test_user_sethandle_valid_multiple(user1,user2):
    user_data_1 = auth_login_v2("caricoleman@gmail.com", "1234567")

    user_data_2 = auth_login_v2("ericamondy@gmail.com", "1234567") 


    assert user_sethandle_v2(user_data_1['token'], 'karikoleman') == {}

    assert  user_profile_v2(user_data_1['token'], user_data_1['auth_user_id']) == {
        'user':
        {
        'u_id': user_data_1['auth_user_id'], 
        'email': "caricoleman@gmail.com", 
        'name_first': 'cari', 
        'name_last': 'coleman', 
        'handle_str': 'karikoleman',
        'profile_img_url': f"{url}static/default.jpg"
        }
    }
    
    assert user_sethandle_v2(user_data_2['token'], 'erikamoney') == {}

    assert  user_profile_v2(user_data_2['token'], user_data_2['auth_user_id']) == {
        'user':
        {
        'u_id': user_data_2['auth_user_id'], 
        'email': "ericamondy@gmail.com", 
        'name_first': 'erica', 
        'name_last': 'mondy', 
        'handle_str': 'erikamoney',
        'profile_img_url': f"{url}static/default.jpg"
        }
    }

# tests for the case when the inputted handle string has less than 3 characters
def test_user_sethandle_invalid_short_handle(user1):
    with pytest.raises(InputError):
        user_data_1 = auth_login_v2("caricoleman@gmail.com", "1234567")

        user_sethandle_v2(user_data_1['token'], 'cc')

# tests for the case when the inputted handle string exceeds the 20 character limit
def test_user_sethandle_invalid_long_handle(user1):
    with pytest.raises(InputError):
        user_data_1 = auth_login_v2("caricoleman@gmail.com", "1234567") 

        user_sethandle_v2(user_data_1['token'], 'cariiiiiiiiiiiiiiiiii')

# tests for the case when the inputted handle string is already being used by another user
def test_user_sethandle_invalid_handle_in_use(user1,user2):
    with pytest.raises(InputError):
        user_data_1 = auth_login_v2("caricoleman@gmail.com", "1234567") 

        user_data_2 = auth_login_v2("ericamondy@gmail.com", "1234567") 


        assert user_sethandle_v2(user_data_1['token'], 'kari') == {}

        assert user_profile_v2(user_data_1['token'], user_data_1['auth_user_id']) == {
            'user':
            {
            'u_id': user_data_1['auth_user_id'], 
            'email': "caricoleman@gmail.com", 
            'name_first': 'cari', 
            'name_last': 'coleman', 
            'handle_str': 'kari',
            'profile_img_url': f"{url}static/default.jpg"
            }
        }
        
        user_sethandle_v2(user_data_2['token'], 'kari') 

# tests the return value of users_all for when only one user is registered
def test_users_all_v1_one(user1):
    
    user_data_1 = auth_login_v2("caricoleman@gmail.com", "1234567") 

    assert users_all(user_data_1['token']) == {
            'users':
            [{
            'u_id': user_data_1['auth_user_id'], 
            'email': "caricoleman@gmail.com", 
            'name_first': 'cari', 
            'name_last': 'coleman', 
            'handle_str': 'caricoleman',
            'profile_img_url': f"{url}static/default.jpg"
            }]
    }

# tests the return value of users_all for when two users are registered
def test_users_all_v1_two(user1,user2):
    user_data_1 = auth_login_v2("caricoleman@gmail.com", "1234567")
    
    assert users_all(user_data_1['token']) == {
            'users':
            [{
            'u_id': user_data_1['auth_user_id'], 
            'email': "caricoleman@gmail.com", 
            'name_first': 'cari', 
            'name_last': 'coleman', 
            'handle_str': 'caricoleman',
            'profile_img_url': f"{url}static/default.jpg"
            },
            {
            'u_id': user2['auth_user_id'], 
            'email': "ericamondy@gmail.com", 
            'name_first': 'erica', 
            'name_last': 'mondy', 
            'handle_str': 'ericamondy',
            'profile_img_url': f"{url}static/default.jpg"
            }]
    } 
    
# tests the return value of users_all for when multiple users are registered
def test_users_all_v1_multiple(user1, user2, user3, user4, user5):
    assert users_all(user1['token']) == {   
            'users':
            [{
            'u_id': user1['auth_user_id'], 
            'email': "caricoleman@gmail.com", 
            'name_first': 'cari', 
            'name_last': 'coleman', 
            'handle_str': 'caricoleman',
            'profile_img_url': f"{url}static/default.jpg"
            },
            {
            'u_id': user2['auth_user_id'], 
            'email': "ericamondy@gmail.com", 
            'name_first': 'erica', 
            'name_last': 'mondy', 
            'handle_str': 'ericamondy',
            'profile_img_url': f"{url}static/default.jpg"
            },
            {
            'u_id': user3['auth_user_id'], 
            'email': "hilarybently@gmail.com", 
            'name_first': 'hillary', 
            'name_last': 'bently', 
            'handle_str': 'hillarybently',
            'profile_img_url': f"{url}static/default.jpg"
            },
            {
            'u_id': user4['auth_user_id'], 
            'email': "kentonwatkins@gmail.com", 
            'name_first': 'kenton', 
            'name_last': 'watkins', 
            'handle_str': 'kentonwatkins',
            'profile_img_url': f"{url}static/default.jpg"
            },
            {
            'u_id': user5['auth_user_id'], 
            'email': "claudiamarley@gmail.com", 
            'name_first': 'claudia', 
            'name_last': 'marley', 
            'handle_str': 'claudiamarley',
            'profile_img_url': f"{url}static/default.jpg"
            },]
        } 
    
def test_users_stats_v1(user1, user2, user3, user4):
    channel1 = channels_create_v1(user1['token'], 'Channel1', True)
    message_send_v1(user1['token'], channel1['channel_id'], "Heyyyy")

    output1 = users_stats_v1(user1['token'])

    assert len(output1['dreams_stats']['channels_exist']) == 2
    assert len(output1['dreams_stats']['dms_exist']) == 1
    assert len(output1['dreams_stats']['messages_exist']) == 2
    assert output1['dreams_stats']['utilization_rate'] == 0.25

    channel_join_v1(user2['token'], channel1['channel_id'])
    channel2 = channels_create_v1(user1['token'], 'Channel2', True)
    dm_create_v1(user1['token'], [user2['auth_user_id']])
    message_send_v1(user1['token'], channel1['channel_id'], "Yo wassup")

    output2 = users_stats_v1(user1['token'])

    assert len(output2['dreams_stats']['channels_exist']) == 3
    assert len(output2['dreams_stats']['dms_exist']) == 2
    assert len(output2['dreams_stats']['messages_exist']) == 3
    assert output2['dreams_stats']['utilization_rate'] == 0.5

    channel_join_v1(user1['token'], channel2['channel_id'])
    channel_join_v1(user3['token'], channel1['channel_id'])

    output3 = users_stats_v1(user1['token'])

    assert len(output3['dreams_stats']['channels_exist']) == 3
    assert len(output3['dreams_stats']['dms_exist']) == 2
    assert len(output3['dreams_stats']['messages_exist']) == 3
    assert output3['dreams_stats']['utilization_rate'] == 0.75

    output4 = message_send_v1(user1['token'], channel1['channel_id'], "Hi")
    message_remove_v1(user1['token'], output4['message_id'])

    output5 = users_stats_v1(user1['token'])

    assert len(output5['dreams_stats']['channels_exist']) == 3
    assert len(output5['dreams_stats']['dms_exist']) == 2
    assert len(output5['dreams_stats']['messages_exist']) == 5
    assert output5['dreams_stats']['utilization_rate'] == 0.75

    dm_create_v1(user4['token'], [user1['auth_user_id']])
    output6 = users_stats_v1(user1['token'])

    assert len(output6['dreams_stats']['channels_exist']) == 3
    assert len(output6['dreams_stats']['dms_exist']) == 3
    assert len(output6['dreams_stats']['messages_exist']) == 5
    assert output6['dreams_stats']['utilization_rate'] == 1

def test_user_stats1_v1(user1,user2):
    channel1 = channels_create_v1(user1[tok], 'Channel1', True)
    channel_join_v1(user2[tok], channel1[cID])
    dm_create_v1(user1[tok], [user2[AuID]])
    message_send_v1(user1[tok], channel1[cID], "Sup")
    
    output = user_stats_v1(user1[tok])
    assert len(output["user_stats"]['channels_joined']) == 2
    assert len(output["user_stats"]['dms_joined']) == 2
    assert len(output["user_stats"]['messages_sent']) == 2
    assert output["user_stats"]["involvement_rate"] == 1


    message = message_send_v1(user2[tok], channel1[cID], "hi")

    output2 = user_stats_v1(user1[tok])

    assert len(output2["user_stats"]['channels_joined']) == 2
    assert len(output2["user_stats"]['dms_joined']) == 2
    assert len(output2["user_stats"]['messages_sent']) == 2
    assert output2["user_stats"]["involvement_rate"] == 0.75


    message_remove_v1(user1[tok], message['message_id'])

    output3 = user_stats_v1(user1[tok])

    assert output3["user_stats"]["involvement_rate"] ==  0.6666666666666666

    message_send_v1(user2[tok], channel1[cID], "hi")
    message_send_v1(user2[tok], channel1[cID], "hi")

    output4 = user_stats_v1(user1[tok])

    
    assert output4["user_stats"]["involvement_rate"] == 0.4

def test_user_stats2_v1(user1,user2, user3):
    dm = dm_create_v1(user1[tok], [user2[AuID]])
    message_senddm_v1(user1[tok], dm[dmID], 'hello meng')

    output = user_stats_v1(user1[tok])

    assert len(output["user_stats"]['channels_joined']) == 1
    assert len(output["user_stats"]['dms_joined']) == 2
    assert len(output["user_stats"]['messages_sent']) == 2
    assert output["user_stats"]["involvement_rate"] == 1

    output = user_stats_v1(user2[tok])

    assert output["user_stats"]["involvement_rate"] == 0.5

    dm_invite_v1(user1[tok], dm[dmID], user3[AuID])
    output2 = user_stats_v1(user3[tok])
    assert len(output2["user_stats"]['messages_sent']) == 1