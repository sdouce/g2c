import requests
from rich import print
import os
from dotenv import load_dotenv

# charge les variables depuis .env
load_dotenv()

GLPI_URL   = os.getenv("GLPI_URL")
USER_TOKEN = os.getenv("GLPI_USER_TOKEN")
APP_TOKEN  = os.getenv("GLPI_APP_TOKEN")


# Headers init
headers = {
    "Content-Type": "application/json",
    "Authorization": f"user_token {USER_TOKEN}",
    "App-Token": APP_TOKEN
}

# 1. Init session
r = requests.get(f"{GLPI_URL}/initSession", headers=headers, verify=False)
session_token = r.json()["session_token"]

headers_session = {
    "Content-Type": "application/json",
    "Session-Token": session_token,
    "App-Token": APP_TOKEN
}


# 2. Récupération des searchOptions
resp = requests.get(f"{GLPI_URL}/listSearchOptions/Computer", headers=headers_session, verify=False)
resp.raise_for_status()
options = resp.json()
# print(options)

criteria = {
    "criteria[0][field]": "1",
    "criteria[0][searchtype]": "equal",
    "criteria[0][value]": "TEST",
    "forcedisplay[0]": "2"
}

search = requests.get(
    f"{GLPI_URL}/search/Computer",
    headers=headers_session,
    params=criteria,
    verify=False
)
data = search.json()
print(data)
comp_id=data['data'][0]['2']
print(comp_id)
computer_dict = requests.get(
    f"{GLPI_URL}/Computer/{comp_id}/Item_OperatingSystem",
    headers=headers_session,
    verify=False
)
print(computer_dict.json())
OS_ID=computer_dict.json()[0]['operatingsystems_id']
OS_DICT = requests.get(
    f"{GLPI_URL}/OperatingSystem/{OS_ID}",
    headers=headers_session,
    verify=False
)
print(OS_DICT.json())

requests.get(f"{GLPI_URL}/killSession", headers=headers_session, verify=False)
