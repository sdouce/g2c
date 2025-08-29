#!/usr/bin/python3.9
# -*- coding: utf-8 -*-

import MySQLdb

class CentreonDB:
    def __init__(self,connection_dico):
        self.dbcnx = MySQLdb.connect(host=connection_dico['host'], user=connection_dico['username'], passwd=connection_dico['password'], port=int(connection_dico['port']), db=connection_dico['base'])
        self.cur = self.dbcnx.cursor()

    def close(self):
        if self.dbcnx:
            self.dbcnx.close()
    def req_get_sysid_in_host_macro(self, SYS_ID):
        query = """
        SELECT host.host_id, host.host_name, host.host_alias, host.host_address 
        FROM centreon.on_demand_macro_host 
        LEFT JOIN host on on_demand_macro_host.host_host_id=host.host_id 
        WHERE host_macro_name='$_HOSTSYS_ID$' 
        AND host_macro_value = %s
        """

        self.cur.execute(query, (SYS_ID,))
        result = self.cur.fetchone()
        return result

    def get_service_info(self, SYS_ID):
        query = f"""
        SELECT 
        host.host_id,
        host.host_name,
        service.service_id,
        service.service_description,
        on_demand_macro_service.svc_macro_value
        FROM centreon.service 
        LEFT JOIN host_service_relation ON host_service_relation.service_service_id = service.service_id
        LEFT JOIN host ON host_service_relation.host_host_id = host.host_id
        INNER JOIN on_demand_macro_service ON on_demand_macro_service.svc_svc_id = service.service_id AND on_demand_macro_service.svc_macro_name = '$_SERVICESYS_ID$' 
        WHERE on_demand_macro_service.svc_macro_value ='{SYS_ID}'
        """
        print(query)
        self.cur.execute(query)
        result = self.cur.fetchone()
        return result

    def get_tpl_id(self, tpl):
        query = f"""select service_id from centreon.service where service_description = '{tpl}'"""
        print(query)

        self.cur.execute(query)
        result = self.cur.fetchone()
        return result
        
    def get_macros(self, id):
        query = f"SELECT * FROM centreon.on_demand_macro_service where svc_svc_id= {id}"
        self.cur.execute(query)
        result = self.cur.fetchall()

        MACROS = {}
        for mac in result:
            if mac[1] in ['$_SERVICEWARN$', '$_SERVICECRIT$']:
                MACROS[mac[1]] = {"id": mac[0], "value": mac[2]}

        return MACROS

    def get_extract_data(self,SHORT_NAME):
        query = f'''
WITH RECURSIVE svc_chain AS (
  SELECT
    centreon.service.service_id            AS leaf_service_id,
    centreon.service.service_id            AS ancestor_service_id,
    0                                       AS depth
  FROM centreon.service
  WHERE centreon.service.service_register = '1'

  UNION ALL

  SELECT
    svc_chain.leaf_service_id,
    centreon.service.service_template_model_stm_id AS ancestor_service_id,
    svc_chain.depth + 1
  FROM svc_chain
  JOIN centreon.service
    ON centreon.service.service_id = svc_chain.ancestor_service_id
  WHERE centreon.service.service_template_model_stm_id IS NOT NULL
),

sev AS (
  SELECT
    svc_chain.leaf_service_id,
    centreon.service_categories.sc_id,
    centreon.service_categories.sc_name,
    centreon.service_categories.level,
    ROW_NUMBER() OVER (
      PARTITION BY svc_chain.leaf_service_id
      ORDER BY centreon.service_categories.level DESC,
               svc_chain.depth ASC,
               centreon.service_categories.sc_id ASC
    ) AS rn
  FROM svc_chain
  JOIN centreon.service_categories_relation
    ON centreon.service_categories_relation.service_service_id = svc_chain.ancestor_service_id
  JOIN centreon.service_categories
    ON centreon.service_categories.sc_id = centreon.service_categories_relation.sc_id
),

eff AS (
  SELECT
    L.leaf_service_id,
    ( SELECT S2.service_max_check_attempts
      FROM svc_chain SC2
      JOIN centreon.service S2 ON S2.service_id = SC2.ancestor_service_id
      WHERE SC2.leaf_service_id = L.leaf_service_id
        AND S2.service_max_check_attempts IS NOT NULL
      ORDER BY SC2.depth ASC LIMIT 1
    ) AS service_max_check_attempts,
    ( SELECT S2.service_normal_check_interval
      FROM svc_chain SC2
      JOIN centreon.service S2 ON S2.service_id = SC2.ancestor_service_id
      WHERE SC2.leaf_service_id = L.leaf_service_id
        AND S2.service_normal_check_interval IS NOT NULL
      ORDER BY SC2.depth ASC LIMIT 1
    ) AS service_normal_check_interval,
    ( SELECT S2.service_retry_check_interval
      FROM svc_chain SC2
      JOIN centreon.service S2 ON S2.service_id = SC2.ancestor_service_id
      WHERE SC2.leaf_service_id = L.leaf_service_id
        AND S2.service_retry_check_interval IS NOT NULL
      ORDER BY SC2.depth ASC LIMIT 1
    ) AS service_retry_check_interval
  FROM (SELECT DISTINCT leaf_service_id FROM svc_chain) AS L
)

SELECT
  centreon.host.host_id,
  centreon.host.host_name,
  centreon.service.service_id,
  centreon.service.service_description,
  sev.level                              AS severity_level,
  sev.sc_name                            AS severity_name,
  eff.service_max_check_attempts,
  eff.service_normal_check_interval,
  eff.service_retry_check_interval,
  centreon_storage.services.notes,
  centreon_storage.services.notes_url,
  centreon_storage.services.action_url,
  centreon_storage.services.command_line
FROM centreon.host
JOIN centreon.host_service_relation
  ON centreon.host_service_relation.host_host_id = centreon.host.host_id
JOIN centreon.service
  ON centreon.service.service_id = centreon.host_service_relation.service_service_id
LEFT JOIN sev
  ON sev.leaf_service_id = centreon.service.service_id
 AND sev.rn = 1
LEFT JOIN eff
  ON eff.leaf_service_id = centreon.service.service_id
LEFT JOIN centreon_storage.hosts
  ON centreon_storage.hosts.name = centreon.host.host_name
LEFT JOIN centreon_storage.services
  ON centreon_storage.services.host_id = centreon_storage.hosts.host_id
 AND centreon_storage.services.description = centreon.service.service_description
WHERE centreon.service.service_register = '1'
  AND centreon.service.service_activate = '1'
  AND centreon.host.host_name LIKE '%{SHORT_NAME}.cloud.cheops.fr'
ORDER BY centreon.host.host_name, centreon.service.service_description;

        '''

        self.cur.execute(query)
        result = self.cur.fetchall()

        return result

    def get_all_client_svc(self,SHORT_NAME):
        query = f'''
        SELECT 
            centreon_storage.hosts.display_name,
            CASE 
                WHEN centreon_storage.services.description LIKE '[ORACLE]%' 
                THEN centreon_storage.services.notes 
                ELSE centreon_storage.hosts.notes 
            END AS notes,
        centreon_storage.services.description,
        centreon_storage.hosts.host_id

        FROM centreon_storage.services
        LEFT JOIN centreon_storage.hosts ON centreon_storage.services.host_id = centreon_storage.hosts.host_id
        WHERE centreon_storage.hosts.display_name LIKE '%{SHORT_NAME}.cloud.cheops.fr'
        AND centreon_storage.services.description not like '%_/%'
        AND centreon_storage.services.description not like '%DISK_/%'
          AND centreon_storage.services.enabled = 1
        '''

        self.cur.execute(query)
        result = self.cur.fetchall()

        return result

    def get_windows_disk_whitout_sysid(self,TYPE):


        if TYPE=="ALL":
            LIGNE_DE_REQUETE=''
        elif TYPE.startswith('HOST'):
            FQDN=TYPE.split(':')[1]            
            LIGNE_DE_REQUETE=f"AND host.host_name = '{FQDN}'"
        elif TYPE.startswith('CLIENT'):
            CLIENT=TYPE.split(':')[1]            
            LIGNE_DE_REQUETE=f"AND host.host_name like '%{CLIENT}'"

        query = f"""
      SELECT
                        host_service_relation.host_host_id,
                        host.host_name,
                        service.service_id,
                        service.service_description,
                        service.service_activate
                    FROM
                        centreon.service
                    LEFT JOIN
                        host_service_relation ON host_service_relation.service_service_id = service.service_id
                    LEFT JOIN
                        host ON host_service_relation.host_host_id = host.host_id

                    WHERE
                        service.service_description LIKE '%DISK\_%'
                        AND service.service_description NOT LIKE '%_QUEUE'
                        AND service.service_description NOT LIKE '%_GAP'
                        AND service.service_description NOT LIKE '%_STATUS'
                        {LIGNE_DE_REQUETE}
                        AND service.service_register != "0"
                        # AND NOT EXISTS (
                        #     SELECT 1
                        #     FROM on_demand_macro_service AS sub
                        #     WHERE sub.svc_svc_id = service.service_id
                        #     AND sub.svc_macro_name = '$_SERVICESYS_ID$'
                        # )

                        """
      

        self.cur.execute(query)
        result = self.cur.fetchall()
        return result
        self.dbcnx.close()
    
    def get_unix_fs_whitout_sysid(self,TYPE):

        if TYPE=="ALL":
            LIGNE_DE_REQUETE=''
        elif TYPE.startswith('HOST'):
            FQDN=TYPE.split(':')[1]            
            LIGNE_DE_REQUETE=f"AND host.host_name = '{FQDN}'"
        elif TYPE.startswith('CLIENT'):
            CLIENT=TYPE.split(':')[1]            
            LIGNE_DE_REQUETE=f"AND host.host_name like '%{CLIENT}'"


        query = f"""
                    SELECT 
                        host_service_relation.host_host_id, 
                        host.host_name,
                        service.service_id,
                        service.service_description,
                        on_demand_macro_service.svc_macro_name,
                        on_demand_macro_service.svc_macro_value,
                        service.service_activate
                    FROM 
                        centreon.service 
                    LEFT JOIN 
                        host_service_relation ON host_service_relation.service_service_id = service.service_id
                    LEFT JOIN 
                        host ON host_service_relation.host_host_id = host.host_id
                    INNER JOIN 
                        on_demand_macro_service 
                            ON on_demand_macro_service.svc_svc_id = service.service_id
                            AND on_demand_macro_service.svc_macro_name = '$_SERVICEFS$'
                    WHERE 
                        service.service_description in ('%FS\_%' | '%INODES\_%')

                        {LIGNE_DE_REQUETE}
                        AND service.service_register != "0"
                        # AND NOT EXISTS (
                        #     SELECT 1
                        #     FROM on_demand_macro_service AS sub
                        #     WHERE sub.svc_svc_id = service.service_id
                        #     AND sub.svc_macro_name = '$_SERVICESYS_ID$'
                        # )
                """


        self.cur.execute(query)
        result = self.cur.fetchall()
        return result
        self.dbcnx.close()
