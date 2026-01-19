import requests

def get_ad_spend_data(access_token, account_id):
    """Get comprehensive ad spend data"""
    base_url = "https://graph.facebook.com/v23.0"
    
    # Get campaigns with insights
    campaigns_url = f"{base_url}/act_{account_id}/campaigns"
    campaigns_response = requests.get(campaigns_url, params={
        'access_token': access_token,
        'fields': 'id,name,status,insights{spend,impressions,clicks,cpm,cpc,ctr,reach,frequency}',
        'time_range': '{"since":"2024-01-01","until":"2025-12-31"}'
    })
    
    print("CAMPAIGNS WITH SPEND:")
    if campaigns_response.status_code == 200:
        campaigns = campaigns_response.json().get('data', [])
        for campaign in campaigns:
            insights = campaign.get('insights', {}).get('data', [])
            spend = insights[0].get('spend', 0) if insights else 0
            print(f"  {campaign['name']}: ${spend}")
    else:
        print(f"  Error: {campaigns_response.text}")
    
    # Get adsets with insights
    adsets_url = f"{base_url}/act_{account_id}/adsets"
    adsets_response = requests.get(adsets_url, params={
        'access_token': access_token,
        'fields': 'id,name,campaign_id,status,insights{spend,impressions,clicks}',
        'time_range': '{"since":"2024-01-01","until":"2025-12-31"}'
    })
    
    print("\nADSETS WITH SPEND:")
    if adsets_response.status_code == 200:
        adsets = adsets_response.json().get('data', [])
        for adset in adsets:
            insights = adset.get('insights', {}).get('data', [])
            spend = insights[0].get('spend', 0) if insights else 0
            print(f"  {adset['name']}: ${spend}")
    else:
        print(f"  Error: {adsets_response.text}")

# Usage - update with new token
if __name__ == "__main__":
    ACCESS_TOKEN = "YOUR_NEW_TOKEN_HERE"
    ACCOUNT_ID = "105849243396571"
    get_ad_spend_data(ACCESS_TOKEN, ACCOUNT_ID)