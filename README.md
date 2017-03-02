# A Python Library for Versature's REST API

[API Documentation] (integrate.versature.com/apidoc/)


##########################################################
### Example - Read active calls for authenticated user ###
##########################################################

```
import versature import Versature

v = Versature(client_id='zzzzzzz', client_secret='xxxxxx')
company_cdrs_for_last_seven_days = v.active_calls(all=True)

```

#######################
### Test Case Setup ###
#######################

Create secret.py config file and add the: URL for Versature's API, Client Id, Client Secret. Also a User, Domain, and Password for each of the roles is needed in order to test

### secret.py 

```
VERSATURE_API_URL = 'https://integrate.versature.com/api'
VERSATURE_CLIENT_ID = ''
VERSATURE_CLIENT_SECRET = ''

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