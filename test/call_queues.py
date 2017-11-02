# -*- coding: utf-8 -*-
import unittest
from datetime import datetime, timedelta

from config import office_manager_config

__author__ = 'DavidWard'


class CallQueuesTest(unittest.TestCase):

    def setUp(self):
        self.office_manager = office_manager_config()
        self.one_day_ago = datetime.utcnow() - timedelta(days=1)
        self.today = datetime.utcnow()

    #################################
    #### Login Call Queue Stats #####
    #################################

    def test_get_call_queues_stats(self):
        result = self.office_manager.versature.call_queue_stats(start_date=self.one_day_ago, end_date=self.today)
        self.assertIsNotNone(result)

    def test_get_call_queues_stats_async(self):
        request = self.office_manager.versature.call_queue_stats(async=True, start_date=self.one_day_ago, end_date=self.today)
        result = request.resolve()
        self.assertIsNotNone(result)
