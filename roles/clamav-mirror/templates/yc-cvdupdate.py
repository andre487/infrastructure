#!/usr/bin/env python3
import json
import os
import subprocess as sp
import urllib.parse
import urllib.request

from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

http = Session()
adapter = HTTPAdapter(max_retries=Retry(total=5, backoff_factor=2, status_forcelist=(429, 500, 502, 503, 504)))
http.mount('http://', adapter)
http.mount('https://', adapter)


def main():
    with open('/etc/proxy-creds.json') as fp:
        proxy_creds = json.load(fp)

    proxy_url = (
        f'https://{urllib.parse.quote(proxy_creds["name"])}:{urllib.parse.quote(proxy_creds["password"])}@'
        '{{ proxy_host }}'
    )
    env = os.environ.copy()
    env['http_proxy'] = env['https_proxy'] = proxy_url
    sp.check_call(['cvdupdate', 'update', '-V'], env=env)

    with open('/var/www/{{ clamav_domain }}/dns.txt') as fp:
        dns_txt = fp.read().strip()

    resp = http.get(
        'http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token',
        headers={'Metadata-Flavor': 'Google'},
    )
    resp.raise_for_status()
    iam_token = resp.json()['access_token']

    resp = http.post(
        'https://dns.api.cloud.yandex.net/dns/v1/zones/{{ yc_dns_zone_id }}:upsertRecordSets',
        headers={'Authorization': f'Bearer {iam_token}'},
        json={
            'replacements': [
                {
                    'name': '{{ yc_dns_record_name }}',
                    'type': 'TXT',
                    'ttl': '300',
                    'data': [f'"{dns_txt}"'],
                },
            ],
        },
    )
    resp.raise_for_status()


if __name__ == '__main__':
    main()
