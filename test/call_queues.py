# -*- coding: utf-8 -*-
import unittest

from config import office_manager_config

__author__ = 'DavidWard'


class CallQueuesTest(unittest.TestCase):

    #################################
    #### Login Call Queue Stats #####
    #################################

    def test_get_call_queues_stats(self):
        result = office_manager_config.versature.call_queue_stats()
        self.assertIsNotNone(result)

    def test_get_call_queues_stats_async(self):
        request = office_manager_config.versature.call_queue_stats(async=True)
        result = request.resolve()
        self.assertIsNotNone(result)