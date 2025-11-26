import json
import boto3
import os
import urllib3

# --- CONFIGURATION ---
SLACK_URL = "https://hooks.slack.com"
# ---------------------

# Connect to LocalStack
endpoint = f"http://{os.environ.get('LOCALSTACK_HOSTNAME', 'localhost')}:4566"
s3 = boto3.client('s3', endpoint_url=endpoint)
http = urllib3.PoolManager()

def lambda_handler(event, context):
    print("Bot v2.0 (Slack Enabled) waking up...")

    bucket_name = "secret-data-bucket"

    # 1. REMEDIATE
    print(f"Scanning bucket: {bucket_name}...")
    try:
        s3.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True
            }
        )
        status = "SUCCESS: Bucket locked down."
    except Exception as e:
        status = f"FAILED: {str(e)}"

    # 2. ALERT SLACK
    print("Sending Slack alert...")
    slack_message = {
        "text": f"🚨 *LocalStack Security Alert* 🚨\n\n**Host:** Ubuntu Server (Wazuh)\n**Target:** {bucket_name}\n**Action:** Public Access Blocked.\n**Status:** {status}"
    }

    try:
        encoded_msg = json.dumps(slack_message).encode('utf-8')
        resp = http.request('POST', SLACK_URL, body=encoded_msg)
        print(f"Slack Status: {resp.status}")
    except Exception as e:
        print(f"Slack Failed: {e}")
        return "Remediation Done, Slack Failed"

    return "Remediation + Alert Sent"
