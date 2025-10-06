import requests
import time
from requests.auth import HTTPBasicAuth


# read parameters from command line arguments
import sys
if len(sys.argv) > 1:
    base_url = sys.argv[1]
    if not base_url.startswith("http://") and not base_url.startswith("https://"):
        base_url = "https://" + base_url
else:
    base_url = "localhost:8089"
if len(sys.argv) > 2:
    splunk_user = sys.argv[2]
else:
    splunk_user = "admin"
if len(sys.argv) > 3:
    splunk_password = sys.argv[3]
else:
    splunk_password = "Password01"

# Configuration
#splunk_user = "admin"
#splunk_password = "Password01"
#base_url = "https://localhost:8002"
verify_ssl = False  # Equivalent to validate_certs: no
import urllib3

# Suppress InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def validate_bundle():
    url = f"{base_url}/services/cluster/manager/control/default/validate_bundle?output_mode=json"
    data = {"check-restart": "true"}
    print("Validating bundle...")
    response = requests.post(
        url,
        data=data,
        auth=HTTPBasicAuth(splunk_user, splunk_password),
        verify=verify_ssl,
        timeout=120
    )
    #response.raise_for_status()
    return response.json()

def get_cluster_info():
    url = f"{base_url}/services/cluster/manager/info?output_mode=json"
    response = requests.get(
        url,
        auth=HTTPBasicAuth(splunk_user, splunk_password),
        verify=verify_ssl
    )
    response.raise_for_status()
    return response.json()

def wait_for_bundle_validation(target_checksum, retries=10, delay=0.5):
    print("Waiting for bundle to be validated...")
    for attempt in range(retries):
        info = get_cluster_info()
        content = info['entry'][0]['content']
        valid_bundle = content.get('last_validated_bundle', {})
        dry_run_bundle = content.get('last_dry_run_bundle', {})
        apply_bundle_status = content['apply_bundle_status']['status']

        is_valid = valid_bundle.get('is_valid_bundle') is True
        validated_checksum = valid_bundle.get('checksum')
        dry_run_checksum = dry_run_bundle.get('checksum')
        last_check_restart_bundle_result = content.get('last_check_restart_bundle_result')

        print(f"Attempt {attempt + 1}/{retries} - Validated checksum: {validated_checksum}, apply_bundle_status, {apply_bundle_status}, Dry run checksum: {dry_run_checksum}, last_check_restart_bundle_result: {last_check_restart_bundle_result}")
        time.sleep(delay)
    
def main():
    bundle_response = validate_bundle()

    # if bundle_response['entry'][0]['content']['checksum'] is not present in the response, raise an error
    if 'checksum' not in bundle_response['entry'][0]['content']:
        print("no new bundle found.")
        exit(-1)

    bundle_checksum = bundle_response['entry'][0]['content']['checksum']
    print(f"Bundle checksum: {bundle_checksum}")
    wait_for_bundle_validation(bundle_checksum)

if __name__ == "__main__":
    main()
