# -*- coding: utf-8 -*-
import unittest

from test.secrets import client_id, username, password, vendor_id
from versature.resources import Versature

__author__ = 'DavidWard'


class BaseAuthenticationTest(unittest.TestCase):

    def setUp(self):
        self.versature = Versature(username=username, password=password, client_id=client_id, vendor_id=vendor_id)

    ########################################
    #### Login With Username & Password ####
    ########################################

    def test_authenticate(self):
        result = self.versature.password_grant(username, password)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result['access_token'])
        self.assertIsNotNone(result['expires_in'])
        self.assertIsNotNone(result['refresh_token'])
        self.assertIsNotNone(result['scope'])
        self.assertEquals(result['token_type'], 'Bearer')

    def test_refresh_token(self):
        result = self.versature.password_grant(username, password)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result['access_token'])
        self.assertIsNotNone(result['expires_in'])
        self.assertIsNotNone(result['refresh_token'])
        self.assertIsNotNone(result['scope'])
        self.assertEquals(result['token_type'], 'Bearer')
        access_token = result['access_token']
        refresh_token = result['refresh_token']

        result = self.versature.refresh_token_grant(refresh_token)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result['access_token'])
        self.assertIsNotNone(result['expires_in'])
        self.assertIsNotNone(result['refresh_token'])
        self.assertIsNotNone(result['scope'])
        self.assertEquals(result['token_type'], 'Bearer')

        self.assertNotEqual(access_token, result['access_token'])
        self.assertEqual(refresh_token, result['refresh_token'])