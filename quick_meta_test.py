import requests

USER_TOKEN = "EAAgVjAbsIWoBPxqMCLqZCJ6snxugFYxPP4nB75tDFuPxvCeZAnlLGwGdet9j7VE97rNUoLmEJWEmWCzJq2Wc0efr7tbDAo8wTXpZCEcZCE0ZCfz2D6CWORx0WPTmcOf8Ea7yu32Nre2Oke9l3QfPaskgxkQcnuQytjWoRb8w4AGcFOi5BkiLypSkIf4BB"
PAGE_ID = "296508423701621"  # BOP Realty

# Get BOP Realty page token
response = requests.get("https://graph.facebook.com/v23.0/me/accounts", params={
    'access_token': USER_TOKEN,
    'fields': 'id,name,access_token'
})

if response.status_code == 200:
    pages = response.json().get('data', [])
    for page in pages:
        if page['id'] == PAGE_ID:
            print(f"BOP Realty Token: {page['access_token']}")
            break
else:
    print(f"Error: {response.text}")