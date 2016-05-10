# -*- coding: utf-8 -*-
import unittest
from integrate.resources import authenitcate

from secrets import client_id, username, password, vendor_id

__author__ = 'DavidWard'


class BaseAuthenticationTest(unittest.TestCase):

    #def setUp(self):
    #    self.google = Google(access_token=GOOGLE_PLACES_KEY)

    ########################################
    #### Login With Username & Password ####
    ########################################

    def test_authenticate(self):
        result = authenitcate.login(username, password, client_id, vendor_id)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result['access_token'])
        self.assertIsNotNone(result['expires_in'])
        self.assertIsNotNone(result['refresh_token'])
        self.assertIsNotNone(result['scope'])
        self.assertEquals(result['token_type'], 'Bearer')

    def test_refresh_token(self):
        result = authenitcate.login(username, password, client_id, vendor_id)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result['access_token'])
        self.assertIsNotNone(result['expires_in'])
        self.assertIsNotNone(result['refresh_token'])
        self.assertIsNotNone(result['scope'])
        self.assertEquals(result['token_type'], 'Bearer')
        access_token = result['access_token']
        refresh_token = result['refresh_token']

        result = authenitcate.refresh_token(refresh_token, client_id, vendor_id)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result['access_token'])
        self.assertIsNotNone(result['expires_in'])
        self.assertIsNotNone(result['refresh_token'])
        self.assertIsNotNone(result['scope'])
        self.assertEquals(result['token_type'], 'Bearer')

        self.assertNotEqual(access_token, result['access_token'])
        self.assertEqual(refresh_token, result['refresh_token'])