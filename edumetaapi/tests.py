import json
from urlparse import urlparse

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.urlresolvers import reverse
from django.test.testcases import TestCase
from django.utils.six import StringIO
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from accounts.models import UserProfile
from edumanage.models import ServiceLoc, Institution, Realm
from edumetaapi.serializers import ServiceLocSerializer, InstitutionSerializer

User = get_user_model()

VALID_LOCATION_DATA = {
    'AP_no': 4711,
    'SSID': 'location ssid',
    'address_street': 'Test St. 1',
    'address_city': 'Test town',
    'latitude': '123.45',
    'longitude': '67.89',
    'NAT': False,
    'IPv6': True,
    'wired': False,
    'port_restrict': False,
    'transp_proxy': False,
}


class LocationViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        realm = Realm.objects.create()
        cls.institution = Institution.objects.create(realmid=realm, ertype=2)
        cls.service_loc = ServiceLoc.objects.create(institutionid=cls.institution, SSID='test ssid', longitude=0,
                                                    latitude=0, IPv6=True,
                                                    wired=False, port_restrict=False, transp_proxy=False, NAT=False,
                                                    AP_no=3, enc_level='WPA2-AES')
        user = User.objects.create()
        UserProfile.objects.create(user=user, institution=cls.institution)
        cls.token = Token.objects.create(user=user)

    def test_get_locations_without_authentication(self):
        url = reverse('location')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_locations_with_authenticated_user(self):
        url = reverse('location')
        response = self.client.get(url, HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content),
                         ServiceLocSerializer(ServiceLoc.objects.filter(institutionid=self.institution.id),
                                              many=True).data)

    def test_get_specific_location_with_authenticated_user(self):
        url = reverse('location', args=[self.service_loc.id])
        response = self.client.get(url, HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content), ServiceLocSerializer(self.service_loc).data)

    def test_get_unknown_location_with_authenticated_user(self):
        url = reverse('location', args=['12345'])
        response = self.client.get(url, HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_new_location_with_authenticated_user(self):
        url = reverse('location')
        response = self.client.post(url, data=VALID_LOCATION_DATA, format='json',
                                    HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_service_loc = ServiceLoc.objects.get(**VALID_LOCATION_DATA)
        self.assertEqual(urlparse(response['Location']).path, reverse('location', args=[created_service_loc.id]))
        self.assertEqual(created_service_loc.institutionid, self.institution)

    def test_post_invalid_location_with_authenticated_user(self):
        data = {
            'foo': 'bar'
        }

        url = reverse('location')
        response = self.client.post(url, data=data, format='json', HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_new_location_without_authentication(self):
        url = reverse('location')
        response = self.client.post(url, data=VALID_LOCATION_DATA, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class InstitutionViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        realm = Realm.objects.create()
        cls.institution = Institution.objects.create(realmid=realm, ertype=3)
        user = User.objects.create()
        UserProfile.objects.create(user=user, institution=cls.institution)
        cls.token = Token.objects.create(user=user)

    def test_get_locations_without_authentication(self):
        url = reverse('institution')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_institution_with_authenticated_user(self):
        url = reverse('institution')
        response = self.client.get(url, HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content),
                         InstitutionSerializer(Institution.objects.get(id=self.institution.id)).data)

    def test_get_specific_institution_with_authenticated_user(self):
        url = reverse('institution', args=[self.institution.id])
        response = self.client.get(url, HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content), InstitutionSerializer(self.institution).data)


class GetTokenTest(TestCase):
    def test_token_for_unknown_user(self):
        out = StringIO()
        username = 'unknown'
        call_command('gettoken', username, stdout=out)
        self.assertIn('Unknown username \'{}\''.format(username), out.getvalue())

    def test_create_new_token_for_user(self):
        out = StringIO()
        username = 'test_user'
        User.objects.create(username=username)
        call_command('gettoken', username, stdout=out)
        token = Token.objects.get(user=User.objects.get(username=username))
        self.assertIn('{}: {}'.format(username, token), out.getvalue())

    def test_get_token_for_user(self):
        out = StringIO()
        username = 'test_user'
        token = Token.objects.create(user=User.objects.create(username=username))
        call_command('gettoken', username, stdout=out)
        self.assertIn('{}: {}'.format(username, token), out.getvalue())

    def test_get_tokens_for_multiple_users(self):
        out = StringIO()
        usernames = [str(i) for i in range(10)]
        tokens = [Token.objects.create(user=User.objects.create(username=username)) for username in usernames]
        call_command('gettoken', *usernames, stdout=out)
        for i, user in enumerate(usernames):
            self.assertIn('{}: {}'.format(user, tokens[i]), out.getvalue())
