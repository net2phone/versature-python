# A python SDK for Versature's API

[API Documentation] (integrate.versature.com/apidoc/)


##########################################################
### Example - Read active calls for authenticated user ###
##########################################################

```
import versature import Versature

v = Versature(username='xxxxxx', password='yyyyy', client_id='zzzzzzz', api_version='1.1.0')
my_active_calls = v.active_calls()

```

#######################
### Test Case Setup ###
#######################

Create secret.py config file and add the: URL for the NetSapiens API, Client Id, Client Secret. Also a User, Domain, and Password for each of the roles is needed in order to test

### secret.py 

```
VERSATURE_API_URL = 'https://integrate.versature.com/api'
VERSATURE_CLIENT_ID = ''

CALL_QUEUE_USER = ''

OFFICE_MANAGER_USER = ''
OFFICE_MANAGER_DOMAIN = ''
OFFICE_MANAGER_PASSWORD = ''

BASIC_USER_USER = ''
BASIC_USER_DOMAIN = ''
BASIC_USER_PASSWORD = ''

RESELLER_USER = ''
RESELLER_DOMAIN = ''
RESELLER_PASSWORD = ''
```