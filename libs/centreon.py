#!/usr/local/bin/python3.7
import requests
import sys
import json
import urllib3
urllib3.disable_warnings()
from rich import print

class payload_gen():
    def __init__(self,dico_ci):
        self.payload_centreon_host={}
        self.dico_ci=dico_ci

    def gen_hostgroups(self,HOSTGROUPS_NAME):
        for HG_NAME in set(HOSTGROUPS_NAME):
            HG=''
            pload_HG='search={"name":"'+ f"{HG_NAME}" +'"}'
            HG=self.dico_ci['CNX_CENTREON_V2'].get_hostgroup_configuration(pload_HG)
            if HG['result']==[]:
                payload_add_hg={"name":f"{HG_NAME}","alias":f"{HG_NAME}"}
                HG_CREATE_ID=self.dico_ci['CNX_CENTREON_V2'].add_hostgroups(payload_add_hg)
                self.dico_ci['centreon_hostgroup_inplace']+=[int(HG_CREATE_ID['id'],)]
            else:
                self.dico_ci['centreon_hostgroup_inplace']+=[int(HG['result'][0]['id'],)]
        return self.dico_ci['centreon_hostgroup_inplace']

    def add_host(self):

        ''' Préparation du payload Centreon pour la création du CI '''
        self.payload_centreon_host={
            "monitoring_server_id": 1, 
            "name": f"{self.dico_ci['fqdn']}", 
            "address": f"{self.dico_ci['ip_address'].lower()}",  
            "alias": f"{self.dico_ci['name']}",
            "templates": [self.dico_ci['HOSTOS_TPL_ID']],
            "groups": self.dico_ci['centreon_hostgroup_inplace'],
        }

        ### GESTION TELEXPLOITATION
        if self.dico_ci['u_tele_exploitation'] == "true":
            self.payload_centreon_host['templates'].insert(0,703)
        ### GESTION TELEXPLOITATION

        self.payload_centreon_host['macros']=[
                {
                    "name": "SYS_ID",
                    "value":  f"{self.dico_ci['sys_id']}",
                    "is_password": False,
                    "description": "ServiceNow CI identifier"
                },
                {
                    "name": "IP_NTP",
                    "value":  f"{self.dico_ci['company_info']['u_ntp_address']}",
                    "is_password": False,
                    "description": "IP de synchro NTP"
                }]

        return self.payload_centreon_host
    
    def update_host(self):
        ''' Préparation du payload Centreon pour la création du CI '''
        self.payload_centreon_host={
            "name": f"{self.dico_ci['fqdn']}", 
            "alias": f"{self.dico_ci['name']}",
            "templates": [self.dico_ci['HOSTOS_TPL_ID']],
            "groups": self.dico_ci['centreon_hostgroup_inplace'],

        }
        self.payload_centreon_host['macros']=self.dico_ci['centreon_macros_inplace']
        self.payload_centreon_host['macros']+=[
                {
                    "name": "SYS_ID",
                    "value":  f"{self.dico_ci['sys_id']}",
                    "is_password": False,
                    "description": "ServiceNow CI identifier"
                }]

        return self.payload_centreon_host
    
    def update_svc(self):
        ''' Préparation du payload Centreon pour la création du CI '''
        self.payload_centreon_host={
            "name": f"{self.dico_ci['fqdn']}", 
            "alias": f"{self.dico_ci['name']}",
            "templates": [self.dico_ci['HOSTOS_TPL_ID']],
            "groups": self.dico_ci['centreon_hostgroup_inplace'],

        }
        self.payload_centreon_host['macros']=[
                {
                    "name": "SYS_ID",
                    "value":  f"{self.dico_ci['sys_id']}",
                    "is_password": False,
                    "description": "ServiceNow CI identifier"
                }]

        return self.payload_centreon_host
    
class centreon_V1():
    def __init__(self,headers,url):
        self.url=url
        self.headers=headers

    def inject_in_centreon(self,body_list):
        for body in body_list:
            req = requests.post(str(self.url)+'?action=action&object=centreon_clapi',headers=self.headers,data=json.dumps(body), verify=False)
            print (req.json())    

    def get_host_params(self,dico_ci):
        body_list=()
        body={'action': 'getparam','object':'host','values': """{centreon_hstname};""".format(**dico_ci)}
        req = requests.post(str(self.url)+'?action=action&object=centreon_clapi',headers=self.headers,data=json.dumps(body), verify=False)
        return req.json()

    def get_host_id(self,dico_ci):
        body_list=()
        body={'action': 'show','object':'host','values': """{fqdn}""".format(**dico_ci)}
        req = requests.post(str(self.url)+'?action=action&object=centreon_clapi',headers=self.headers,data=json.dumps(body), verify=False)
        return req.json()
    def get_host_macros(self,dico_ci):
        body_list=()
        body={'action': 'getmacro','object':'host','values': """{fqdn}""".format(**dico_ci)}
        req = requests.post(str(self.url)+'?action=action&object=centreon_clapi',headers=self.headers,data=json.dumps(body), verify=False)
        return req.json()

    def get_svc_macros(self,dico_ci):
        body_list=()
        body={'action': 'getmacro','object':'service','values': """{fqdn};{service}""".format(**dico_ci)}
        req = requests.post(str(self.url)+'?action=action&object=centreon_clapi',headers=self.headers,data=json.dumps(body), verify=False)
        return req.json()
    
    def add_svc_macros(self,dico_ci):
        body_list=()
        body={'action': 'setmacro','object':'service','values': """{fqdn};{service};{macroname};{value}""".format(**dico_ci)}
        req = requests.post(str(self.url)+'?action=action&object=centreon_clapi',headers=self.headers,data=json.dumps(body), verify=False)
        return req.json()

class centreon_V2():
    def __init__(self, url, api, version):
        self.url = url
        self.version=version
        if url.startswith('http://172.17.24.3'):
            self.API_TOKEN=api
            self.headers = {"X-AUTH-TOKEN": f"{self.API_TOKEN}"}
        else:
            if self.url =='https://centreonqual.infocheops.local/centreon/api/':
                payload= '{"security": {"credentials": {"login": "admin","password": "@AZOPqslm@2345"}}}'
                # print(payload)
                self.version='beta'
            else:
                payload= '{"security": {"credentials": {"login": "admin","password": "@AZOPqslm@2345"}}}'
            self.headers = {'Content-Type': 'application/json'}
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            requ = requests.post(url+'beta/login',headers=self.headers ,data=str(payload), verify=False)
        
            try:
                requ.raise_for_status()
            except requests.exceptions.HTTPError as e:
                print (e)
            json = requ.json()
            print(json)
            self.headers['X-AUTH-TOKEN'] = json['security']['token']

    # FONCTIONS DE TYPE CREATION/UPDATE
    def add_host(self, payload):
        add_host = f'{self.url}{self.version}/configuration/hosts'
        host_centreon = requests.post(add_host, headers=self.headers,data=json.dumps(payload), verify=False)
        return host_centreon.status_code, host_centreon.json()
    
    def add_hostgroups(self, payload):
        add_hostgroups = f'{self.url}{self.version}/configuration/hosts/groups'
        host_group = requests.post(add_hostgroups, headers=self.headers,data=json.dumps(payload), verify=False)

        return host_group.json()
    
    def add_service(self, payload):
        add_service = f'{self.url}{self.version}/configuration/services'
        add_service_centreon = requests.post(add_service, headers=self.headers,data=json.dumps(payload), verify=False)
        return add_service_centreon.status_code, add_service_centreon.json()
    
    def update_host(self, payload, HOST_CENTREON_ID):
        update_host = f'{self.url}{self.version}/configuration/hosts/{HOST_CENTREON_ID}'
        host_centreon = requests.patch(update_host, headers=self.headers,data=json.dumps(payload), verify=False)
    
        return host_centreon
    
    def update_service(self, payload,SERVICE_CENTREON_ID):
        add_service = f'{self.url}{self.version}/configuration/services/{SERVICE_CENTREON_ID}'
        add_service_centreon = requests.patch(add_service, headers=self.headers,data=json.dumps(payload), verify=False)

        return add_service_centreon.status_code
    
    def deploy_services(self,host_id):        
        host_deploy=f'{self.url}{self.version}/configuration/hosts/{host_id}/services/deploy'
        host_centreon = requests.post(host_deploy,headers=self.headers,verify=False)
        # return host_centreon.json()

    # FONCTIONS DE TYPE RECUPERATION DE CONFIGURATION CENTREON 
    def get_host2210_configuration(self,payload): 
        host = f'{self.url}{self.version}/monitoring/hosts/{payload}'
        host_centreon = requests.get(host, headers=self.headers, verify=False)
        return host_centreon.json()
    
    def get_hosts_configuration(self,payload):        
        host = f'{self.url}{self.version}/configuration/hosts?{payload}'
        host_centreon = requests.get(host, headers=self.headers, verify=False)
        return host_centreon.json()
    
    def get_hostgroup_configuration(self, payload):        
        host = f'{self.url}{self.version}/configuration/hosts/groups?{payload}'
        host_centreon = requests.get(host, headers=self.headers, verify=False)
        return host_centreon.json()
    
    def get_htpl_configuration(self, payload):        
        host = f'{self.url}{self.version}/configuration/hosts/templates?{payload}'
        host_centreon = requests.get(host, headers=self.headers, verify=False)
        return host_centreon.json()
    
    def get_stpl_configuration(self, payload):        
        stpl = f'{self.url}{self.version}/configuration/services/templates?{payload}'
        stpl_centreon = requests.get(stpl, headers=self.headers, verify=False)
        return stpl_centreon.json()

    def get_services_configuration(self, payload):        
        host_downtime=f'{self.url}{self.version}/configuration/services?{payload}'
        host_centreon = requests.get(host_downtime,headers=self.headers,verify=False)
        return host_centreon.json()
    
    def get_services_monitoring(self, payload):        
        host_downtime=f'{self.url}{self.version}/monitoring/services?{payload}'
        host_centreon = requests.get(host_downtime,headers=self.headers,verify=False)
        return host_centreon.json()
    
    def get_host_service_configuration(self, host_id, svc_name):     
        payload = f'search={{"$and":[{{"host.id":"{host_id}"}},{{"name":"{svc_name}"}}]}}'   
        host_svc=f'{self.url}{self.version}/configuration/services?{payload}'
        host_centreon = requests.get(host_svc,headers=self.headers,verify=False)
        return host_centreon.json()
    
    def find_good_integration_poller():
        print()
