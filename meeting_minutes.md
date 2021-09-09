*************************************************************************************************************************************************
** Prior discussion of agenda was done through Facebook Messenge so meeting consisted mainly of co-coding and helping each other finalise code **
*************************************************************************************************************************************************

Iteration 2 begins here:
8/3/21
Attendance: Nick Liu, Ethan Kwong, Jeffrey Meng, Vincent Le and Nick Lam
    Meeting to go through spec together
    Discuss branching system and any changes to be made from iteration 1
    More progress checks 
    Functionalise code that all members can use to make their functions more ‘clean’
    Universal legend for all files

17/3/21 
Attendance: Nick Liu, Ethan Kwong, Jeffrey Meng, Vincent Le and Nick Lam
    Began discussion of iteration 2, delegations of task and how it would work holistically 
    Changing iteration 1: 
        Old functions auth_register_v1→needs to redo the implementation of user_ids
        Old function channel_join_v1 → needs to redo the implementation of channel_ids 
        Everyone those the flask wrap around for the functions they implemented in iteration 1
    Iteration 2 functions:
        Nick Liu - message/send/v2, message/edit/v2, message/remove/v2, channel/leave/v1
        Nick Lam / Ethan Kwong - dm/details/v1, dm/listv1, dm/create/v1, dm/remove/v1, dm/invite/v1, dm/leave/v1, dm/messages/v1, message/senddm/v1
        Vincent Le - message/share/v2, admin/permission/change/v1, channel/addowner/v1, channel/removeowner/v1
        Jeffrey Meng - user/profile/v2, user/profile/setname/v2, user/profile/setemail/v2, user/profile/sethandle/v1, user/all/v1, admin/user/remove/v1
    Began discussing how to implement a data structure to implement the notifications function
        Notifications should be placed within the user data structure
        Each user dictionary should contain a key named notifications containing a list 
        Each time there is a message within a dm or channel the user is a part of, this information will be inserted into the notification data structure within their user dictionary
        When notifications is called, the function returns the first 20 notifications within the list from the back

19/3/21 
Attendance: Nick Liu, Ethan Kwong, Jeffrey Meng, Vincent Le and Nick Lam
    Group meeting where we fixed all pylint errors in order to pass the pipeline. Discussed different tests that would enable use to increase the coverage of our code

Feedback from Xiaocong (Gary)
    Fixtures
    Need comments in testing files
    Labels for taskboard


Release of Results - Iteration 1 (20/03/21)
(list of things to fix for next iteration)
    channels_list and channels_listall
        Change return dictionary key to ‘name’ instead of ‘channel_name’

21/3/21 
Attendance: Nick Liu, Ethan Kwong, Jeffrey Meng, Vincent Le and Nick Lam
Discuss: where to put HTTP functions
Set due date for finishing 80% functions- 28/3/21

28/3/21
Attendance: Nick Liu, Ethan Kwong, Vincent Le and Nick Lam
    Went through dm functions as a group
    Ethan, Nick Lam pair programmed message/senddm and dm/messages

29/3/21
Attendance: Nick Liu, Jeffrey Meng, Vincent Le and Nick Lam
    Helped Jeffrey Meng finish his functions
    Merged his work into master
    Others bug fixed their functions

31/3/21
Attendance: Nick Liu, Ethan Kwong, Vincent Le and Nick Lam
    Fixed up pylint of functions
    Deliverable: Fix up coverage of each person's function
    Discussed notifications_get and search
    Notifications: New list containing dictionary- 1st key- user_id, 2nd key- notification
    Within notification- containing channel id, dm id and message
    Message send, dm send, and share need a tagging function
    Standups where each member talked about their desired method of storing notifications
        The structure the group decided on was to use a dictionary of dictionaries where each key was a u_id corresponding to a list of notifications


3/4/21
Attendance: Nick Liu, Ethan Kwong, Jeffrey Meng, Vincent Le and Nick Lam
    Implemented everyone’s base functions 
    Began discussing HTTP testing and functions
        Each person do their functions http testing
        Set date to finish by next meeting 4/4
    Discussion of persistence 
        JSON vs Pickle
        Weighing up pros and cons of each
        Decided to go with JSON

4/4/21
Attendance: Nick Liu, Ethan Kwong, Jeffrey Meng, Vincent Le and Nick Lam
    Continued working and coding through http tests together 
    Persistence and coverage checkup 
        Progress check
    Discussed everyone's expected deadlines to ensure that iteration 2 would be finished on time

5/4/21
Attendance: Nick Liu, Ethan Kwong, Jeffrey Meng, Vincent Le and Nick Lam
    Finalised everyone’s http tests and did final merge for submission of iteration 2
        Finished working on persistence branch too
    Ensured pylint, coverage and pytests were all passing
    Reread through comments and doc strings to ensure quality
    Pointed out that spec wanted ‘handle_str’ and not ‘handle_string’
        Changed all instances of ‘handle_string’ to ‘handle_str’ and merged it into master
    Wrote up assumptions document
    Discussed things to work on for iteration 3

7/4/21
Attendance: Nick Liu, Ethan Kwong, Jeffrey Meng, Vincent Le and Nick Lam
Time 11-12:00am
    Iteration 3 released
    Co-reading of the spec and discussion
    broke down the tasks and assigned functions and workload
        Vincent and Meng: analytics
        Nick Liu: Message send later
        Nick lam and Ethan: reacts and pins
    Also work was planned for interviewing,
    Hoping to find people for interview ASAP
    Discussed deployment

9/4/21
Attendance: Nick Liu, Ethan Kwong, Jeffrey Meng, Vincent Le and Nick Lam
    Interviews
    Two interviewees were conducted and our notes from the interview was discussed
    Allocated work for the Planning documentation
    In the meeting we also briefly broke down:
        - Use Cases
        - small discussion on the functions needed and HTTP request
        
13/4/21
Attendance: Nick Liu, Ethan Kwong, Jeffrey Meng, Vincent Le and Nick Lam
Time: 11 -1:30 am
    Discussed how to fix assertion errors for iteration 2 so that iteration 3 will work:
    Add something into decode such that it checks permission ID and will raise AccessErrors accordingly
    E.g. for Remove_user
    When user is removed, remove them from all channels and DMs
    In users_all, do not append users with user_permission_id = 0
    auth/logout is raising InputError when it shouldn’t
    Test_can_have_two_sessions
    Test_successful_logout
    Test_not_logged_in_logout
    Test_invalid_token
    test_invalidated_token
    When inviting global_owners, make sure to add them to channel[‘owner_members’]
    test_invite_global_owner
    When join channels for global_owners, make sure to add them to channel[‘owner_members’]
    Test_global_owner_join_channel_public
    When joining private channels for global_owners, make sure to add them to channel[‘owner_members’]
    Test_global_owner_join_channel_private
    Owners of a channel can leave freely
    Test_member_leave_channel_successfully
    Error being raised in message_edit
    Test_removal_by_edit_reflected
    Test_nonmember_cannot_remove_owner
    Check tests for channel_removeowner
    Test_cannot_edit_deleted_message
    Check that shared message tags
    Test_tag_thru_message_share_triggers_notification
    Check that when adding a owner_member triggers a notif
    Write tests for this

    Test_http_admin_user_remove_valid
    Change channel_messages and dm_messages for edge cases
    Fixed http tests but cbbs fixing normal tests
    Change dm_invite test
    I think ive fixed all of these
    Change hard coded tests (who GAF if its circular definitions)
    Fixed my DM test ones
    Come back to search function
    Channel and dm_details

    For our next sub-iteration: 
        Standups - Ethan and Nicks
        Profile - Vincent and Jeffrey

16/4/21
Attendance: Nick Liu, Ethan Kwong, Jeffrey Meng, Vincent Le and Nick Lam
    Reinterview of our user cases
    Noted down some limitations in their needs
        - No offline capabilities etc
    Had a short debrief after interview to discuss our documentation
    Small checkup on coding progress of our assigned functions
    User and Dreams analytics successfully implemented
    Message react and pin successfully implemented.

17/4/21
Attendance: Nick Liu, Ethan Kwong, Jeffrey Meng, Vincent Le and Nick Lam

    Started on userprofile/upload and standups
    Coding done throughout the day, periodic meetings and standup meetings to discuss
    Changes in data structures proposed and implementing more helper functions

18/4/21
Attendance: Nick Liu, Ethan Kwong, Jeffrey Meng, Vincent Le and Nick Lam
    Started implementation of password reset functions
    General meetings throughout the day for checkups and standup meetings
    Worked in subgroups for the SDLC pdf and coding, alternating

19/4/21
Attendance: Nick Liu, Ethan Kwong, Jeffrey Meng, Vincent Le and Nick Lam
Time: 11am-1:30 am
    Day spent on wrapping up and general life-style bug fixes
    Most of the merges to master was discussed and finalised today
    Deployment night, 
        - wrapping up, 
        - bugfixing, 
        - code review,
        - Assumptions.

More details can be found at:
    https://docs.google.com/document/d/1GIzf-JhN33HH3dEVvG0U6j_GUUdKqp4hqIfOrDVuXBA/edit?usp=sharing 
