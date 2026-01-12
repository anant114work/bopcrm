import requests
import hashlib
import hmac
import json
import os
from datetime import datetime
from .acefone_models import AcefoneConfig, DIDNumber

class AcefoneClient:
    def __init__(self):
        self.access_key = "YOUR_ACCESS_KEY"
        self.secret_key = "YOUR_SECRET_KEY"
        self.region = "ap-south-1"
        self.service = "execute-api"
        self.base_url = "https://api.acefone.in"
        self.host = "api.acefone.in"
        
        # Use your actual AWS credentials for PBX API
        # These should be set in your Acefone account
        self.access_key = os.getenv("ACEFONE_ACCESS_KEY", "YOUR_ACCESS_KEY")
        self.secret_key = os.getenv("ACEFONE_SECRET_KEY", "YOUR_SECRET_KEY")
    
    def _sign(self, key, msg):
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()
    
    def _get_signature_key(self, key, date_stamp, region_name, service_name):
        kDate = self._sign(("AWS4" + key).encode('utf-8'), date_stamp)
        kRegion = self._sign(kDate, region_name)
        kService = self._sign(kRegion, service_name)
        kSigning = self._sign(kService, "aws4_request")
        return kSigning
    
    def _acefone_request(self, method, endpoint, payload=""):
        url = self.base_url + endpoint
        
        now = datetime.utcnow()
        amz_date = now.strftime('%Y%m%dT%H%M%SZ')
        date_stamp = now.strftime('%Y%m%d')
        
        canonical_uri = endpoint
        payload_hash = hashlib.sha256(payload.encode('utf-8')).hexdigest()
        canonical_headers = f"host:{self.host}\nx-amz-date:{amz_date}\n"
        signed_headers = "host;x-amz-date"
        
        canonical_request = f"{method}\n{canonical_uri}\n\n{canonical_headers}\n{signed_headers}\n{payload_hash}"
        
        algorithm = "AWS4-HMAC-SHA256"
        credential_scope = f"{date_stamp}/{self.region}/{self.service}/aws4_request"
        string_to_sign = f"{algorithm}\n{amz_date}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"
        
        signing_key = self._get_signature_key(self.secret_key, date_stamp, self.region, self.service)
        signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
        
        authorization_header = f"{algorithm} Credential={self.access_key}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
        
        headers = {
            "x-amz-date": amz_date,
            "Authorization": authorization_header,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        print(f"ACEFONE: {method} {url}")
        
        if method == "GET":
            return requests.get(url, headers=headers)
        else:
            return requests.post(url, data=payload, headers=headers)
    
    # PBX API methods removed - not available with Click-to-Call Support token
    # These require AWS signature authentication which Support API doesn't have:
    # - fetch_my_numbers() 
    # - sync_numbers_to_db()
    # - get_active_calls()
    # - get_call_status()
    
    def _initiate_pbx_call(self, from_number, to_number):
        """Initiate click-to-call using PBX API with AWS signature"""
        payload = json.dumps({
            "from": from_number,
            "to": to_number
        })
        
        try:
            response = self._acefone_request("POST", "/v1/calls/click-to-call", payload)
            print(f"PBX CALL: Status {response.status_code}, Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json() if response.content else {"success": True}
                return {"success": True, "data": data}
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    

    
