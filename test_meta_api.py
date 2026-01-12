import requests

# Test Meta API
token = "EAAgVjAbsIWoBP43VKAVme0Gjo6I73BFspx0zP2mHn2VhRND1pJxiVraFZBWDBy0EDYgkwgpBi44ZCDoPTf49au5vIPBTtAmotauuZCNOx69nmZCcUjOkiZC9a1MIgflc5TYHj4ZBgGHtzzimtYOUfuz75Ghncd8l8EmzZA1YTT034gBeDnPsRtSesGBTJZB82ipP"
page_id = "296508423701621"

# Test token validity
url = f"https://graph.facebook.com/v18.0/me?access_token={token}"
response = requests.get(url)
print(f"Token test: {response.status_code} - {response.text}")

# Test lead forms
url = f"https://graph.facebook.com/v18.0/{page_id}/leadgen_forms?access_token={token}"
response = requests.get(url)
print(f"Forms test: {response.status_code} - {response.text}")

if response.status_code == 200:
    data = response.json()
    print(f"Found {len(data.get('data', []))} forms")
else:
    print("Meta API not working - token may be expired")