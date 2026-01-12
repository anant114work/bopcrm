import requests

pages = [
    ("The Great Indian Property Show", "724725327387557", "EAAgVjAbsIWoBP2xF8ss9IJt8wUX1yZCptYmIGcf2VYYJzC29APADNeJHENrb8dehZCfHtNitDfwa08jbv3ZAXYznexsS3odiD8YeTk79wJC6mFuMdd5YuouZAlwLyyit122QbJxRDe7tZC2VuAN2Tv2skFxUhCbuSZA5qZAursMeqtPrWy2jNNPhrWZC0NZCZCyZAZCoZAS0sZAOlyi3Um4wugfs3KreW1VrSDEYC4BUq5lfe9ChkA"),
    ("BOP Realty", "296508423701621", "EAAgVjAbsIWoBPwbu2rqXClBx8yxAhWL4QxH0rRUWLrApwFRLOEuS14kQfTOIR5ZCMQb8OAMAIytZBcCtGwpQHSkOIo8myugk4avGTQzg0BZCkV1tdSNIJRxVkJwtO4ZA7vSF7cauw4YtJ3bgLlfVJppgZCeyaRjPFijDmZAX5qyh5vTZA2B54pjV3ZCZBNpyCjOMmgqkHhOlLY9Kl1GlblcqZBcesPfHaZBTzx8FxZCNcte56Jwn"),
    ("Migsun Rohini", "289710667565750", "EAAgVjAbsIWoBPyX7OE88triTEaZAqyI24S3yFeKZAsJuj49hj02LXRwcaIoZANcFZAVvdK2b3NsODetv5W03ExXfxBH4kKxAz0ZC2J8uDemxG5ZC31lZAfF4e1KC2vLcjwYd2UqDiVmMRW2xwf0ggTxsmz02GWNUHGZARh6ZBdc4kAvudbyRiZB22hQ6yBmB2oNHRq364wE0RlaxKAFrdvZB9FHkEA5RHZAMPCfXGvcwymSZA66Yf")
]

for name, page_id, token in pages:
    print(f"\nChecking {name} (ID: {page_id}):")
    
    # Check forms
    forms_response = requests.get(f"https://graph.facebook.com/v23.0/{page_id}/leadgen_forms", params={
        'access_token': token,
        'fields': 'id,name,status,leads_count'
    })
    
    if forms_response.status_code == 200:
        forms = forms_response.json().get('data', [])
        print(f"  Forms: {len(forms)}")
        
        total_leads = 0
        for form in forms:
            leads_count = form.get('leads_count', 0)
            total_leads += leads_count
            print(f"    {form['name']}: {leads_count} leads")
        
        print(f"  Total leads: {total_leads}")
    else:
        print(f"  Error: {forms_response.text}")