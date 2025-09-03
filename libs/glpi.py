import requests
from rich import print
import os
from dotenv import load_dotenv



class glpi_api():
    def __init__(self,cnx_snow):
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

    def get_one_or_none_item_from_table(self,dico_to_look):
        '''
        Fonction d'update général d un ci dans une table
        '''
        snow_table =  self.cnx_snow.resource(api_path='/table/'+ dico_to_look['snow_table'])
        CI_RETURN_ONE=snow_table.get(query=dico_to_look['snow_query']).one_or_none()
        return CI_RETURN_ONE
