import os

# Optional: without a key (or with the "not_available" placeholder written by
# deploy_docker.sh) the Yahoo provider is disabled instead of crashing at import.
_key = os.environ.get('RAPIDAPI_KEY', '').strip()
RAPIDAPI_CONFIGURED = bool(_key) and _key != 'not_available'

APIDOJO_APIKEYS = {
    'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com",
    'x-rapidapi-key': _key,
}
