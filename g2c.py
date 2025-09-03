import requests
from rich import print
import os,sys
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


criteria = {
    "criteria[0][field]": "1",
    "criteria[0][searchtype]": "equal",
    "criteria[0][value]": "mauresque",
    "forcedisplay[0]": "2"
}

search = requests.get(
    f"{GLPI_URL}/search/Computer",
    headers=headers_session,
    params=criteria,
    verify=False
)
data = search.json()


comp_id=data['data'][0]['2']


computer_dict = requests.get(
    f"{GLPI_URL}/Computer/{comp_id}?with_disks=true",
    headers=headers_session,
    verify=False
)
DICO_GLPI=computer_dict.json()
print(DICO_GLPI)
sys.exit()

computer_dict_OS = requests.get(
    f"{GLPI_URL}/Computer/{comp_id}/Item_OperatingSystem",
    headers=headers_session,
    verify=False
)
print(computer_dict_OS.json())


OS_ID=computer_dict_OS.json()[0]['operatingsystems_id']
OS_DICT = requests.get(
    f"{GLPI_URL}/OperatingSystem/{OS_ID}",
    headers=headers_session,
    verify=False
)
print(OS_DICT.json())


DICO_GLPI['OS']=OS_DICT.json()
print(DICO_GLPI)

requests.get(f"{GLPI_URL}/killSession", headers=headers_session, verify=False)
