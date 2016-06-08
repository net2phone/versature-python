# -*- coding: utf-8 -*-
import unittest

from test.config import office_manager_config

__author__ = 'DavidWard'


class BaseAuthenticationTest(unittest.TestCase):

    ########################################
    #### Login With Username & Password ####
    ########################################

    def test_authenticate(self):
        result = office_manager_config.versature.password_grant(office_manager_config.username, office_manager_config.password)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result['access_token'])
        self.assertIsNotNone(result['expires_in'])
        self.assertIsNotNone(result['refresh_token'])
        self.assertIsNotNone(result['scope'])
        self.assertEquals(result['token_type'], 'Bearer')

    def test_refresh_token(self):
        result = office_manager_config.versature.password_grant(office_manager_config.username, office_manager_config.password)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result['access_token'])
        self.assertIsNotNone(result['expires_in'])
        self.assertIsNotNone(result['refresh_token'])
        self.assertIsNotNone(result['scope'])
        self.assertEquals(result['token_type'], 'Bearer')
        access_token = result['access_token']
        refresh_token = result['refresh_token']

        result = office_manager_config.versature.refresh_token_grant(refresh_token)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result['access_token'])
        self.assertIsNotNone(result['expires_in'])
        self.assertIsNotNone(result['refresh_token'])
        self.assertIsNotNone(result['scope'])
        self.assertEquals(result['token_type'], 'Bearer')

        self.assertNotEqual(access_token, result['access_token'])
        self.assertEqual(refresh_token, result['refresh_token'])