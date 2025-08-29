#!/usr/local/bin/python3.7
import hvac, os,sys ,pysnow,requests
from datetime import datetime,timedelta
from rich import print
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.padding import Padding
from rich.panel import Panel
from rich.progress import track
from text_unidecode import unidecode

class snow_req():
    def __init__(self,cnx_snow):
        self.cnx_snow=cnx_snow

    def get_one_or_none_item_from_table(self,dico_to_look):
        '''
        Fonction d'update général d un ci dans une table
        '''
        snow_table =  self.cnx_snow.resource(api_path='/table/'+ dico_to_look['snow_table'])
        CI_RETURN_ONE=snow_table.get(query=dico_to_look['snow_query']).one_or_none()
        return CI_RETURN_ONE
    
    def get_all_item_from_table(self,dico_to_look_all):
        '''
        Fonction d'update général d un ci dans une table
        '''
        snow_table =  self.cnx_snow.resource(api_path='/table/'+ dico_to_look_all['snow_table'])
        CI_RETURN_ALL=snow_table.get(query=dico_to_look_all['snow_query']).all()
        return CI_RETURN_ALL
    

    def update_item_in_table(self,dico_to_update):
        '''
        Fonction d'update général d un ci dans une table
        '''

        snow_table =  self.cnx_snow.resource(api_path='/table/'+dico_to_update['snow_table'])
        updated_record = snow_table.update(query={'sys_id': dico_to_update['sys_id']}, payload=dico_to_update['payload'])
        return updated_record
   

    def delete_item_in_table(self,dico_to_delete):
        '''
        Fonction d'update général d un ci dans une table
        '''
        snow_table =  self.cnx_snow.resource(api_path='/table/'+dico_to_delete['snow_table'])
        print(dico_to_delete['number'])
        updated_record = snow_table.delete(query={'number': dico_to_delete['number']})
        return updated_record
   