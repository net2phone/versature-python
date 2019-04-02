import os

API_URL = 'https://integrate.versature.com/api'
API_VERSION = '1.7.0'
CLIENT_ID = os.getenv('VERSATURE_CLIENT_ID', None)
CLIENT_SECRET = os.getenv('VERSATURE_CLIENT_SECRET', None)
VENDOR_ID = os.getenv('VERSATURE_VENDOR_ID', None)
