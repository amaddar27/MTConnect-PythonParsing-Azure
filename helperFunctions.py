import sys
from datetime import datetime
import requests
from requests.exceptions import ConnectionError, HTTPError, Timeout
from xml.dom.minidom import parseString
from time import sleep
from termcolor import colored  # not entirely necessary just for aesthetics
# from azure.iot.device import IoTHubDeviceClient, Message

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # make more secure in implementation



def getNextSequence(dom):
    header = dom.getElementsByTagName('Header')[0]
    return header.getAttribute('nextSequence'), header.getAttribute('bufferSize')


def convert(timestamp):
    return datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')


def sendToAzureHub(data):
    print(colored(data, 'blue'))    # blue for Azure


def retry(retries):
    wait = retries * 10
    print('Failed. Waiting %s secs and re-trying...' % wait)
    print("--------------------------------------------------")
    sys.stdout.flush()
    sleep(wait)
    retries += 1
    return retries

def statusCheck(retry_status):
    if retry_status:
        print("~~~Reconnected~~~")
        return False

def getDom(url, max_retries):
    if max_retries < 1:
        max_retries = 1
    retries = 1
    retried = False
    success = False
    while not success and retries <= max_retries:
        try:
            r = requests.get(url, verify=False, timeout=10)
            r.raise_for_status()
            retried = statusCheck(retried)
            response = parseString(r.text)
            success = True
            return response
        except (HTTPError, ConnectionError, Timeout) as e:
            print(e)
            retries = retry(retries)
            retried = True
            if retries == max_retries + 1:
                raise SystemExit(e)
        except Exception as e:
            print("Unexpected error")
            raise SystemExit(e)