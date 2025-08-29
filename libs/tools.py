#!/usr/local/bin/python3.7
import argparse
from rich_argparse import RichHelpFormatter
import socket
from rich.console import Console
from rich.table import Table
from rich import print
from rich.syntax import Syntax
from rich.progress import track
import sys
import inquirer
import re


def get_args_tool():
    """
    Supports the command-line arguments listed below.
    """

    parser = argparse.ArgumentParser(description='Intégration d un CI computer de ServiceNow vers Centreon', formatter_class=RichHelpFormatter)

    parser.add_argument('-E', '--envi',  required=False,default="POC", action='store', help='Environnement CENTREON DEV/QUAL/PROD/POC')
    parser.add_argument('-H', '--host',  required=False,default="ALL", action='store', help='Environnement CENTREON DEV/QUAL/PROD/POC')
    parser.add_argument('-C', '--client',  required=False,default="ALL", action='store', help='Environnement CENTREON DEV/QUAL/PROD/POC')
    parser.add_argument('-D', '--debug',  required=False,choices=['yes', 'no'],default='no', action='store', help='Si --debug pour les test')

    args = parser.parse_args()
    return args
def get_args_fs_sysid():
    """
    Supports the command-line arguments listed below.
    """

    parser = argparse.ArgumentParser(description='Gestion du Drive Windows ou Filesysteme Unix/Linux', formatter_class=RichHelpFormatter)

    parser.add_argument('-S', '--sys_id',  required=True, action='store', help='sys_id du drive ou fs de la table cmdb_ci_file_system ')
    parser.add_argument('-E', '--envi',  required=False,default="POC", action='store', help='Environnement CENTREON DEV/QUAL/PROD/POC')
    parser.add_argument('-D', '--debug',  required=False,choices=['yes', 'no'], default='yes', action='store', help='Si --debug pour les test')

    """"""
    args = parser.parse_args()
    return args

def get_args():
    """
    Supports the command-line arguments listed below.
    """

    parser = argparse.ArgumentParser(description='Intégration d un CI computer de ServiceNow vers Centreon', formatter_class=RichHelpFormatter)
    parser.add_argument('-F', '--fqdn', required=True, action='store', help='Concerned HOST')
    parser.add_argument('-E', '--envi',  required=False,default="POC", action='store', help='Environnement CENTREON DEV/QUAL/PROD/POC')
    parser.add_argument('-t', '--type',  required=False,choices=[None,'cluster','lan','oracle','virtu'], action='store', help='Pour les Objets Type \nvcenter / cluster / oravip / remote / fw/ sw / fcsw /ap  et autre ... ')
    parser.add_argument('-D', '--debug',  required=False,choices=['yes', 'no'],default='no', action='store', help='Si --debug pour les test')
    parser.add_argument('-U', '--update',  required=False,choices=['yes', 'no'],default='no', action='store', help='Si --udpate yes Services seront alors mis à jour ')
    parser.add_argument('-S', '--SID',  required=False,default=None, action='store', help='Si --udpate yes Services seront alors mis à jour ')

    args = parser.parse_args()
    return args

def final_output(dico_ci):
    payload_svc = 'limit=10000&search={"host.id":"'+ f"{dico_ci['centreon_host_id']}" +'"}'
    RESULTAT_FINAL=dico_ci['CNX_CENTREON_V2'].get_services_configuration(payload_svc)
    sorted_result = sorted(RESULTAT_FINAL['result'], key=lambda svc: svc['name'])
    table = Table(title=dico_ci['fqdn'])

    table.add_column("Type", justify="right", style="cyan", no_wrap=True)
    table.add_column("Name", style="magenta")
    table.add_column("Status", style="green")
    table.add_row('HOST', "PING")
    
    for svc in  (sorted_result):
        if svc['is_activated'] is True :
            table.add_row('SVC', svc['name'],'[green]Enabled')
        else:
            table.add_row('SVC', svc['name'],'[red]Disabled')


    console = Console(record=True)
    console.export_html()
    console.print(table)


def compare_output(SYS_ALREADY_IN_CENTREON,dico_ci):
    table = Table(title="Comparaison SNOW / CENTREON")

    table.add_column("CHAMPS", justify="right", style="cyan", no_wrap=True)
    table.add_column("SERVICENOW", style="magenta")
    table.add_column("CENTREON", style="green")
    if dico_ci['fqdn'] != SYS_ALREADY_IN_CENTREON[1]:
        table.add_row('Nom FQDN', '[green]'+dico_ci['fqdn'],'[red]'+SYS_ALREADY_IN_CENTREON[1])
    if dico_ci['name'].split('.')[0] != SYS_ALREADY_IN_CENTREON[2]:
        table.add_row('Alias', '[green]'+dico_ci['name'].split('.')[0],'[red]'+SYS_ALREADY_IN_CENTREON[2])
    else:
        table.add_row('Alias', '[green]'+dico_ci['name'].split('.')[0],'[green]'+SYS_ALREADY_IN_CENTREON[2])
    if dico_ci['ip_address'] != SYS_ALREADY_IN_CENTREON[3]:
        table.add_row('IP', '[green]'+dico_ci['ip_address'],'[red]'+SYS_ALREADY_IN_CENTREON[3])
    else:
        table.add_row('IP', '[green]'+dico_ci['ip_address'],'[green]'+SYS_ALREADY_IN_CENTREON[3])

    console = Console(record=True)
    console.export_html()
    console.print(table)


def getIP(fqdn):
        """
        This method returns the first IP address string
        that responds as the given domain name
        """
        try:
            data = socket.gethostbyname(fqdn)
            ip = repr(data)
            return str(ip).strip('\'')
        except Exception:
            # fail gracefully!
            return False

