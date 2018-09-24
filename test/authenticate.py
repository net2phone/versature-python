# -*- coding: utf-8 -*-
import unittest

from test.config import access_config

__author__ = 'DavidWard'


class BaseAuthenticationTest(unittest.TestCase):

    ########################################
    #### Login With Username & Password ####
    ########################################

    def test_authenticate(self):
        result = access_config.office_manager.versature.password_grant(access_config.office_manager.username,
                                                                       access_config.office_manager.password)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result['access_token'])
        self.assertIsNotNone(result['expires_in'])
        self.assertIsNotNone(result['refresh_token'])
        self.assertIsNotNone(result['scope'])
        self.assertEquals(result['token_type'], 'Bearer')

    def test_refresh_token(self):
        result = access_config.office_manager.versature.password_grant(access_config.office_manager.username,
                                                                       access_config.office_manager.password)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result['access_token'])
        self.assertIsNotNone(result['expires_in'])
        self.assertIsNotNone(result['refresh_token'])
        self.assertIsNotNone(result['scope'])
        self.assertEquals(result['token_type'], 'Bearer')
        access_token = result['access_token']
        refresh_token = result['refresh_token']

        result = access_config.office_manager.versature.refresh_token_grant(refresh_token)
        self.assertIsNotNone(result)
        self.assertIsNotNone(result['access_token'])
        self.assertIsNotNone(result['expires_in'])
        self.assertIsNotNone(result['refresh_token'])
        self.assertIsNotNone(result['scope'])
        self.assertEquals(result['token_type'], 'Bearer')

        self.assertNotEqual(access_token, result['access_token'])
        self.assertEqual(refresh_token, result['refresh_token'])
