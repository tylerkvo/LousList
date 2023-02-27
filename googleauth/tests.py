from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User

from urllib.parse import urlencode

"""
NOTE TO WINSTON FROM WINSTON: run test cases with --keepdb flag
                                remember to use two dashes:
                                    
                                    $> python .\manage.py test --keepdb
                            
                                STOP FORGETTING!!!
"""

# Create your tests here.

"""
This is here because my machine is fucked and I need to make sure
    the test case is actually working
"""
"""
class TestCaseTest(TestCase):
    def test_test_test(self):
        a = True
        self.assertTrue(a)  # Obviously this should return true
"""

"""
NOTE TO WINSTON FROM WINSTON: a period in the terminal output when running test cases 
                              means that it passed
"""

"""
Important Notes:
    - get and post requests should have secure=True to work with the security features of Django
    - Make sure to delete models made for the tests, as the database isn't deleted after each run
    - setUp runs before each individual test_func, while tearDown runs right after
    - each test function needs to begin with 'test'
"""


class LoginIndexViewTests(TestCase):
    """
    This test checks to see if login screen is viewable
    """

    def test_is_page_available(self):
        response = self.client.get(reverse("login"), secure=True)
        self.assertEqual(response.status_code, 200)


class AboutViewTests(TestCase):
    """
    This test checks to see if the about page is viewable
    Assert statement has a 302 code because the about page should redirect to a relatively bare
        welcome screen if the user is not logged in
    """

    def test_is_page_available(self):
        response = self.client.get(reverse("about"), secure=True)
        self.assertEqual(response.status_code, 302)

    """
    This test checks the about page for a user that is logged in
    Assertion 200 status code because the about page should only be fully viewable when logged in
    """

    def test_is_page_available_logged_in(self):
        user1 = User.objects.create(username="user1")
        user1.set_password("password")
        user1.save()

        self.client.login(username="user1", password="password")
        response = self.client.get(reverse("about"), secure=True)
        self.assertEqual(response.status_code, 200)

        self.client.logout()
        user1.delete()


class ProfileViewTests(TestCase):

    def setUp(self):
        self.client = Client()

        user1 = User.objects.create(username='user1')
        user1.set_password('password')
        user1.save()

        user2 = User.objects.create(username="user2")
        user2.set_password('password2')
        user2.save()

    # https://stackoverflow.com/questions/49626899/django-secure-ssl-redirect-breaks-unit-tests-that-use-the-in-built-client
    # Django SECURE_SSL_REDIRECT breaks unit tests that use the in-built client
    # Author: David Downes

    """
    Tests that the edit page leads to a 302 code when not logged in
    Fails otherwise
    """

    def test_is_page_available(self):
        response = self.client.get(reverse("profile"), secure=True)
        self.assertEqual(response.status_code, 302)

    """
    Tests if the page is available while signed in
    """

    def test_is_page_available_logged_in(self):
        self.client.login(username="user1", password="password")
        response = self.client.get(reverse("profile"), secure=True)

        self.assertEqual(response.status_code, 200)

        self.client.logout()

    """
    This test visits a specific user profile when not logged in
    Fails if not redirected (not 302)
    """

    def test_visit_profile_not_logged_in(self):
        response = self.client.get('/profile/8', secure=True)
        self.assertEqual(response.status_code, 302)

    """
    This test creates a user and visits their profile page
    fails if loading the page gives an error
    """

    def test_visit_profile_logged_in(self):
        user1 = User.objects.get(username="user1")

        self.client.login(username="user1", password="password")
        response = self.client.get('/profile/' + str(user1.socialuser.id), secure=True)

        self.assertEqual(response.status_code, 200)

        self.client.logout()

    # https://stackoverflow.com/questions/2619102/djangos-self-client-login-does-not-work-in-unit-tests
    # Django's self.client.login(...) does not work in unit tests
    # Author: Pedro M Duarte

    """
    Visits non-existent profile while signed in
    Fails if it doesn't return 404 or if 10,000 users are created to get id = 10000
    """

    def test_visit_non_existent_profile(self):
        self.client.login(username="user1", password="password")
        response = self.client.get('/profile/10000', follow=True, secure=True)

        self.assertEqual(response.status_code, 404)

        self.client.logout()

    """
    Visits another users profile while signed in
    Fails if it doesn't return 200
    """

    def test_visit_anothers_profile(self):
        user2 = User.objects.get(username="user2")

        self.client.login(username="user1", password="password")
        response = self.client.get('/profile/' + str(user2.socialuser.id), secure=True)

        self.assertEqual(response.status_code, 200)

        self.client.logout()

    """
    Adds a friend (follows a user) to a user using the view/link, not direct model adding
    Fails if user2 isn't in user1's friends field
    """

    def test_add_friend(self):
        user1 = User.objects.get(username="user1")
        user2 = User.objects.get(username="user2")

        is_friend = user2 in user1.socialuser.friends.all()

        self.assertEqual(len(user1.socialuser.friends.all()), 0)
        self.assertEqual(is_friend, False)

        self.client.login(username="user1", password="password")
        response = self.client.get('/add_friend/' + str(user2.socialuser.id), secure=True)

        is_friend = user2 in user1.socialuser.friends.all()

        self.assertEqual(len(user1.socialuser.friends.all()), 1)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(is_friend, True)

        self.client.logout()

    """
    Adds nonexistent friend (attempts to follow a user) using the view/link
    Fails if user1's friends field has an added entry or if there's another error (or if there is an 
        actual user with id = 10000)
    """

    def test_add_null_friend(self):
        user1 = User.objects.get(username="user1")
        user2 = User.objects.get(username="user2")

        is_friend = user2 in user1.socialuser.friends.all()

        self.assertEqual(len(user1.socialuser.friends.all()), 0)
        self.assertEqual(is_friend, False)

        self.client.login(username="user1", password="password")
        response = self.client.get('/add_friend/10000', secure=True)

        is_friend = user2 in user1.socialuser.friends.all()

        self.assertEqual(len(user1.socialuser.friends.all()), 0)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(is_friend, False)

        self.client.logout()

    """
    Adds a friend currently on a user's friendlist again (adds the other user first)
    Fails if the number of friends on user1's friendlist change
    """

    def test_add_friend_again(self):
        user1 = User.objects.get(username="user1")
        user2 = User.objects.get(username="user2")

        is_friend = user2 in user1.socialuser.friends.all()

        self.assertEqual(len(user1.socialuser.friends.all()), 0)
        self.assertEqual(is_friend, False)

        self.client.login(username="user1", password="password")
        response = self.client.get('/add_friend/' + str(user2.socialuser.id), secure=True)

        is_friend = user2 in user1.socialuser.friends.all()

        self.assertEqual(len(user1.socialuser.friends.all()), 1)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(is_friend, True)

        response = self.client.get('/add_friend/' + str(user2.socialuser.id), secure=True)

        is_friend = user2 in user1.socialuser.friends.all()

        self.assertEqual(len(user1.socialuser.friends.all()), 1)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(is_friend, True)

        self.client.logout()

    """
    Tests that you can't use the add friend functionality signed out
    Fails if code is not 302 or error
    """

    def test_add_friend_logged_out(self):
        response = self.client.get('/add_friend/1', secure=True)
        self.assertEqual(response.status_code, 302)

    """
    Removes a friend already on a user's friend list (the user is following the user on the list)
    Fails if the friend isn't removed from user1's friendlist
    """

    def test_remove_friend(self):
        user1 = User.objects.get(username="user1")
        user2 = User.objects.get(username="user2")

        self.client.login(username="user1", password="password")
        response = self.client.get('/add_friend/' + str(user2.socialuser.id), secure=True)

        is_friend = user2 in user1.socialuser.friends.all()

        self.assertEqual(len(user1.socialuser.friends.all()), 1)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(is_friend, True)

        response = self.client.get('/remove_friend/' + str(user2.socialuser.id), secure=True)

        is_friend = user2 in user1.socialuser.friends.all()

        self.assertEqual(len(user1.socialuser.friends.all()), 0)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(is_friend, False)

        self.client.logout()

    """
    Attempts to remove a friend that does not exist
    Fails if user1's friendlist is altered in any way (or if there's a user with id = 10000)
    """

    def test_remove_null_friend(self):
        user1 = User.objects.get(username="user1")
        user2 = User.objects.get(username="user2")

        is_friend = user2 in user1.socialuser.friends.all()

        self.assertEqual(len(user1.socialuser.friends.all()), 0)
        self.assertEqual(is_friend, False)

        self.client.login(username="user1", password="password")
        response = self.client.get('/add_friend/' + str(user2.socialuser.id), secure=True)

        is_friend = user2 in user1.socialuser.friends.all()

        self.assertEqual(len(user1.socialuser.friends.all()), 1)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(is_friend, True)

        response = self.client.get('/remove_friend/10000', secure=True)

        is_friend = user2 in user1.socialuser.friends.all()

        self.assertEqual(len(user1.socialuser.friends.all()), 1)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(is_friend, True)

        self.client.logout()

    """
    Attempts to remove a friend that exists twice
    Fails if an error is thrown or if the friendlist to user1 is altered
    """

    def test_remove_friend_again(self):
        user1 = User.objects.get(username="user1")
        user2 = User.objects.get(username="user2")
        user3 = User.objects.create(username="user3")
        user3.set_password('password3')
        user3.save()

        is_friend = user2 in user1.socialuser.friends.all()

        self.assertEqual(len(user1.socialuser.friends.all()), 0)
        self.assertEqual(is_friend, False)

        self.client.login(username="user1", password="password")
        response = self.client.get('/add_friend/' + str(user2.socialuser.id), secure=True)

        is_friend = user2 in user1.socialuser.friends.all()

        self.assertEqual(len(user1.socialuser.friends.all()), 1)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(is_friend, True)

        response = self.client.get('/add_friend/' + str(user3.socialuser.id), secure=True)

        is_friend = user2 in user1.socialuser.friends.all() and user3 in user1.socialuser.friends.all()

        self.assertEqual(len(user1.socialuser.friends.all()), 2)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(is_friend, True)

        response = self.client.get('/remove_friend/' + str(user2.socialuser.id), secure=True)

        is_friend = user2 in user1.socialuser.friends.all()

        self.assertEqual(len(user1.socialuser.friends.all()), 1)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(is_friend, False)

        response = self.client.get('/remove_friend/' + str(user2.socialuser.id), secure=True)

        is_friend = user2 in user1.socialuser.friends.all()

        self.assertEqual(len(user1.socialuser.friends.all()), 1)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(is_friend, False)

        user3.delete()

        self.client.logout()

    """
    Tests that you can't use the remove friend functionality signed out
    Fails if code is not 302 or error
    """

    def test_remove_friend_logged_out(self):
        response = self.client.get('/remove_friend/1', secure=True)
        self.assertEqual(response.status_code, 302)

    """
    This test tests the functionality of the username and bio editing functionality
    Fails if there's an error or if the user data is unchanged (or changed incorrectly)
    """

    def test_edit_profile(self):
        user1 = User.objects.get(username="user1")

        self.client.login(username="user1", password="password")
        data = urlencode({"username": "userOne", "bio": "This is a bio!"})
        response = self.client.post('/profile', data=data, content_type="application/x-www-form-urlencoded",
                                    secure=True)

        self.assertEqual(response.status_code, 302)
        user1.refresh_from_db()
        self.assertEqual(user1.username, "userOne")
        self.assertEqual(user1.socialuser.bio, "This is a bio!")

        user1.username = "user1"
        user1.save()

        self.client.logout()

    def tearDown(self):
        user1 = User.objects.get(username="user1")
        user2 = User.objects.get(username="user2")

        user1.delete()
        user2.delete()


class ScheduleViewTests(TestCase):

    def setUp(self):
        self.client = Client()

        user1 = User.objects.create(username='user1')
        user1.set_password('password')
        user1.save()

        user2 = User.objects.create(username="user2")
        user2.set_password('password2')
        user2.save()

    def test_is_page_available(self):
        response = self.client.get(reverse("schedulelist"), secure=True)
        self.assertEqual(response.status_code, 302)

    """
    Tests that the page can be visited when signed in
    Fails if response code is not 200
    """

    def test_is_page_available_logged_in(self):
        self.client.login(username="user1", password="password")
        response = self.client.get(reverse("schedulelist"), secure=True)
        self.assertEqual(response.status_code, 200)

        self.client.logout()

    """
    Tests that a schedule for a user can be created
    Fails if the new schedule is not found
    """

    def test_create_schedule(self):
        user1 = User.objects.get(username="user1")

        self.client.login(username="user1", password="password")
        data = urlencode({"name": "test_schedule"})
        response = self.client.post('/addschedule', data=data, content_type="application/x-www-form-urlencoded",
                                    secure=True)

        self.assertEqual(response.status_code, 302)
        user1.refresh_from_db()
        self.assertEqual(len(user1.socialuser.schedule_set.all()), 1)
        self.assertEqual(user1.socialuser.schedule_set.all()[0].name, "test_schedule")

        self.client.logout()

    """
    Tests if the user can visit the page of their created schedule
    Fails if it returns a code other than 200 or if the schedule doesn't exist
    """

    def test_visit_schedule(self):
        user1 = User.objects.get(username="user1")

        self.client.login(username="user1", password="password")
        data = urlencode({"name": "test_schedule"})
        response = self.client.post('/addschedule', data=data, content_type="application/x-www-form-urlencoded",
                                    secure=True)

        self.assertEqual(response.status_code, 302)
        user1.refresh_from_db()
        self.assertEqual(len(user1.socialuser.schedule_set.all()), 1)
        schedlist = user1.socialuser.schedule_set.all()
        self.assertEqual(schedlist[0].name, "test_schedule")

        response = self.client.get('/schedule/' + str(schedlist[0].id), secure=True)

        self.assertEqual(response.status_code, 200)

        self.client.logout()

    """
    Tests if another user can visit a separate user's schedule (doesn't matter if following)
    Fails if they can't (code not 200)
    """

    def test_visit_other_schedule(self):
        user2 = User.objects.get(username="user2")

        self.client.login(username="user2", password="password2")
        data = urlencode({"name": "test_schedule"})
        self.client.post('/addschedule', data=data, content_type="application/x-www-form-urlencoded",
                         secure=True)

        schedlist = user2.socialuser.schedule_set.all()

        self.client.logout()
        self.client.login(username="user1", password="password")

        response = self.client.get('/schedule/' + str(schedlist[0].id), secure=True)

        self.assertEqual(response.status_code, 200)

        self.client.logout()

    """
    Tests that the addschedule page can't be access when logged out
    Fails if it returns a code not 302
    """

    def test_create_schedule_logged_out(self):
        response = self.client.get('/addschedule', secure=True)
        self.assertEqual(response.status_code, 302)

    """
    Tests that a schedule can be removed
    Fails if the schedule still exists
    """

    def test_remove_schedule(self):
        user1 = User.objects.get(username="user1")

        self.client.login(username="user1", password="password")
        data = urlencode({"name": "test_schedule"})
        response = self.client.post('/addschedule', data=data, content_type="application/x-www-form-urlencoded",
                                    secure=True)

        self.assertEqual(response.status_code, 302)
        user1.refresh_from_db()
        self.assertEqual(len(user1.socialuser.schedule_set.all()), 1)
        self.assertEqual(user1.socialuser.schedule_set.all()[0].name, "test_schedule")

        response = self.client.post('/deleteschedule/' + str(user1.socialuser.schedule_set.all()[0].id), secure=True)

        self.assertEqual(response.status_code, 302)
        user1.refresh_from_db()
        self.assertEqual(len(user1.socialuser.schedule_set.all()), 0)

        self.client.logout()

    """
    Tests that you can't remove a non-existent schedule
    Fails if an error is thrown or if it doesn't return 404 (or if a user has id=10000)
    """

    def test_remove_null_schedule(self):
        self.client.login(username="user1", password="password")
        response = self.client.get('/deleteschedule/10000', secure=True)

        self.assertEqual(response.status_code, 404)

        self.client.logout()
    
    """
    Tests that the website redirects when trying to use the deleteschedule link logged out
    Fails if code is not 302
    """
    def test_remove_schedule_logged_out(self):
        response = self.client.get('/deleteschedule/10000', secure=True)
        self.assertEqual(response.status_code, 302)
        
    """
    This test visits 'schedule1' created by the admin account
    This test will fail if either the schedule is deleted or the admin user is deleted
    Test is currently failing before it says the status code is 404, but web browser says it's 200
    """
    """
    def test_visit_jacob_schedule(self):
        user = User.objects.create_user('user', 'user@email.com', 'password')
        self.client.force_login(user)
        response = self.client.get('/schedule/11')
        self.assertEqual(response.status_code, 200)
    """

    def test_visit_schedule_not_logged_in(self):
        response = self.client.get('/schedule/11', secure=True)
        self.assertEqual(response.status_code, 302)

    def tearDown(self):
        user1 = User.objects.get(username="user1")
        user2 = User.objects.get(username="user2")

        user1.delete()
        user2.delete()


class SearchViewTests(TestCase):

    def test_is_page_available(self):
        response = self.client.get(reverse("search"), secure=True)
        self.assertEqual(response.status_code, 302)


class InterestedClassListTests(TestCase):
    """
    Test case checks to see if the url for an existing class code exists
    Possibly update this in the future to also test the button press for adding a class to interested list
    """

    def test_add_valid_class(self):
        response = self.client.get('/interested/ASTR-1210-10334', follow=True, secure=True)
        self.assertEqual(response.status_code, 200)

    """
    Test case checks to see if url for a bogus class fails to fetch a successful response
    Test is currently passing because manually typing URL into browser bar and hitting enter will render
        the interested class template with the parameters injected into the URL.
    """
    """
    def test_add_nonexistent_class(self):
        response = self.client.get('/interested/CS-9696-12345', follow=True)
        self.assertNotEqual(response.status_code, 200)
    """
