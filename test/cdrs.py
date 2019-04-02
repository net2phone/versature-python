# -*- coding: utf-8 -*-
import unittest
from datetime import datetime, timedelta

from config import access_config


__author__ = 'DavidWard'


class CDRsTest(unittest.TestCase):

    def setUp(self):
        self.one_day_ago = datetime.utcnow() - timedelta(days=1)

    ##################
    #### Get CDRs ####
    ##################

    def test_calls_answer(self):
        result = access_config.office_manager.versature.answer_call(call_id='33333333333', to='126m@versature.com')
        self.assertIsNotNone(result)

    def test_get_cdrs_for_domain_office_manager(self):
        result = access_config.office_manager.versature.cdrs(start_date=self.one_day_ago)
        self.assertIsNotNone(result)

    def test_get_cdrs_for_user_office_manager(self):
        result = access_config.office_manager.versature.cdrs(user=access_config.office_manager.user, start_date=self.one_day_ago)
        self.assertIsNotNone(result)

    def test_client_credential_domain_cdrs(self):
        result = access_config.client_credentials.versature.cdrs(start_date=self.one_day_ago)
        self.assertIsNotNone(result)
