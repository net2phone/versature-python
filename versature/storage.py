# -*- coding: utf-8 -*-

import json
from datetime import datetime, timedelta, date

__author__ = 'DavidWard'


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))


class Storage(object):
    """
    Base class to extend when implementing a storage backend.
    """

    def create_storage_key(self, path, params, data):
        """
        Generate a key for this type of request
        :return:
        """
        params_hash = hash(json.dumps(params, sort_keys=True, default=json_serial)) if params else 0
        data_hash = hash(json.dumps(data, sort_keys=True, default=json_serial)) if data else 0
        return '{name}_{param_hash}_{data_hash}'.format(name=path, param_hash=abs(params_hash), data_hash=abs(data_hash))

    def get(self, key):
        """
        Get the provided item from storage

        :param str key: the key to get the counter value for
        """
        raise NotImplementedError

    def set(self, key, value, timeout=None):
        """
        Add the key to the dict storage for the timeout period.

        :param key:
        :param value:
        :param timeout:
        :return:
        """
        raise NotImplementedError

    def delete(self, key):
        """
        Remove the provided key from storage

        :param key:
        :return:
        """
        raise NotImplementedError


class DictionaryStorage(Storage):

    NO_TIMEOUT = 'No Timeout'

    def __init__(self):
        self.storage_dict = dict()
        self.expiry_dict = dict()

    def get(self, key):
        """
        Get the provided item from storage

        :param str key: the key to get the counter value for
        """
        expires = self.expiry_dict.get(key, None)
        result = self.storage_dict.get(key, None)

        if result and expires and (expires == self.NO_TIMEOUT or expires > datetime.utcnow()):
            return result
        else:
            self.expiry_dict.pop(key, None)
            self.storage_dict.pop(key, None)

    def set(self, key, value, timeout=None):
        """
        Add the key to the dict storage for the timeout period. None means
        :param key:
        :param value:
        :param timeout:
        :return:
        """
        self.storage_dict[key] = value

        if timeout:
            self.expiry_dict[key] = datetime.utcnow() + timedelta(seconds=timeout)
        else:
            self.expiry_dict[key] = self.NO_TIMEOUT

    def delete(self, key):
        """
        Remove the provided key from storage
        :param key:
        :return:
        """
        self.expiry_dict.pop(key, None)
        self.storage_dict.pop(key, None)