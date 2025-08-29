#!/usr/local/bin/python3.7
import hvac, os ,pysnow,requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

class cnx():
    def __init__(self):

        os.environ['REQUESTS_CA_BUNDLE'] = '/etc/ssl/certs/ca-bundle.crt'
        role_id_cli = os.getenv("VAULT_ROLE_ID_CLI")
        secret_id_cli = os.getenv("VAULT_SECRET_ID_CLI")
        role_id_clicred = os.getenv("VAULT_ROLE_ID_CLI_CRED")
        secret_id_clicred = os.getenv("VAULT_SECRET_ID_CLI_CRED")
        vault_addr = os.getenv("VAULT_ADDR", "https://vault.example.com")  # valeur par défaut

        client = hvac.Client(url=vault_addr)
        client_cred = hvac.Client(url=vault_addr)
        client.auth.approle.login(role_id_cli,secret_id_cli)
        client_cred.auth.approle.login(role_id_clicred,secret_id_clicred)

        self.client=client
        self.client_cred=client_cred

    def get_password_from_user_path_vault(self,mountpoint,path,user):
        secret = self.client_cred.secrets.kv.v2.read_secret_version(mount_point=mountpoint,path=path)
        PASSWORD=secret['data']['data'][user]
        return PASSWORD

    def db_mysql_cent(self,envi,base):
        centreon_secret_mysql = self.client.read(f'outils-kv/data/centreon/{envi}/mysql')
        dico_my={
            "host":centreon_secret_mysql['data']['data']['ip'],
            "username":centreon_secret_mysql['data']['data']['username'],
            "password":centreon_secret_mysql['data']['data']['password'],
            "port":centreon_secret_mysql['data']['data']['port'],
            "base":base
        }
        return dico_my
  
    
    def snow_access(self,envi):

        '''CONNEXION SERVICENOW PAR VAULT ==> PROD'''
        snow_secret = self.client.read(f'outils-kv/data/servicenow/{envi}/api')
        sn_user=snow_secret['data']['data']['username']
        sn_pwd=snow_secret['data']['data']['password']
        s = requests.Session()
        s.auth = requests.auth.HTTPBasicAuth(sn_user,sn_pwd)
        adapter = HTTPAdapter(
        max_retries=Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=(401, 408, 429, 431, 500, 502, 503, 504, 511)
            )
        )
        s.mount('https://', adapter)
        c = pysnow.Client(instance='cheops', session=s)
        return c

    
    def centreon_access_apiV1(self,envi):        
        '''CONNEXION CENTREON PAR VAULT ==> PROD'''
        centreon_secret = self.client.read(f'outils-kv/data/centreon/{envi}/api')
        user=centreon_secret['data']['data']['username']
        password=centreon_secret['data']['data']['password']
        url=centreon_secret['data']['data']['url_api_v1'] 
        payload= {'username': user,'password': password}
        request = requests.post(str(url)+'?action=authenticate', data=payload, verify=False)

        try:
            request.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print (e)

        token = request.json()['authToken']  # assign the authToken to a variable named token

        dico_ctn_v1={
                "token": token,  # use the variable token instead of undefined 'token'
                "headers":    {'Content-Type': 'application/json','centreon-auth-token': token},
                "url":url # same here
        }
        return dico_ctn_v1
    
    def centreon_access_apiV2(self,envi):
     
        '''CONNEXION CENTREON PAR VAULT ==> POC'''
        centreon_secret = self.client.read(f'outils-kv/data/centreon/{envi}/api')
        dico_ctn_v2={
            "api": centreon_secret['data']['data']['apikey'],
            "url":centreon_secret['data']['data']['url_api_v2']
        }
        return dico_ctn_v2

    
