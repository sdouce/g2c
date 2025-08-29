import sqlite3

class DatabaseManager:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.cursor = self.conn.cursor()

    def create_the_table(self, table_name, fields):
        fields_str = ', '.join([f'{k} {v}' for k, v in fields.items()])
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({fields_str})"
        self.cursor.execute(query)
        self.conn.commit()

    def insert_into_table(self, table_name, data):
        keys_str = ', '.join(data.keys())
        values_str = ', '.join(['?' for _ in data.values()])
        query = f"INSERT INTO {table_name} ({keys_str}) VALUES ({values_str})"
        self.cursor.execute(query, tuple(data.values()))
        self.conn.commit()

    def update_table(self, table_name, set_data, where_data):
        import ast

        # Check if set_data is a string and convert it to a dict if it is
        if isinstance(set_data, str):
            set_data = ast.literal_eval(set_data)

        # Check if where_data is a string and convert it to a dict if it is
        if isinstance(where_data, str):
            where_data = ast.literal_eval(where_data)

        # Create the SET part of the SQL statement
        set_parts = []
        for key in set_data.keys():
            part = f'{key} = ?'
            set_parts.append(part)
        set_str = ', '.join(set_parts)  # Removed .format(*set_data.values())

        # Create the WHERE part of the SQL statement
        where_parts = []
        for key in where_data.keys():
            part = f'{key} = ?'
            where_parts.append(part)
        where_str = ' AND '.join(where_parts)

        # Combine everything into an SQL UPDATE statement
        query = f"UPDATE {table_name} SET {set_str} WHERE {where_str}"

        # Execute the query
        self.cursor.execute(query, (*set_data.values(), *where_data.values()))

        # Print the query for debugging
        print(query, (*set_data.values(), *where_data.values()))

        # Commit the changes
        self.conn.commit()

    def select_from_table(self, table_name, where_data):
        # Constructing a query
        query = f"SELECT * FROM {table_name} WHERE "
        # Adding conditions from where_data
        for key in where_data:
            query += f"{key} = ? AND "
        # Removing last ' AND '
        query = query[:-4]
        # Executing the query
        self.cursor.execute(query, tuple(where_data.values()))
        query = query+';'
        # Fetching results
        rows = self.cursor.fetchone()
        return rows



    def delete_from_table(self, table_name, where_data):
        where_str = ' AND '.join([f'{k} = ?' for k in where_data.keys()])
        query = f"DELETE FROM {table_name} WHERE {where_str}"
        self.cursor.execute(query, tuple(where_data.values()))
        self.conn.commit()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS diskdrives(
                            centreon_hstid TEXT,
                            centreon_svcid TEXT,
                            centreon_activate TEXT,
                            snow_id TEXT,
                            centreon_hstname TEXT,
                            centreon_svcname TEXT,
                            snow_appstatus TEXT,
                            snow_apptype TEXT,
                            snow_related_ci TEXT,
                            snow_moved TEXT,
                            snow_monitor TEXT,
                            json_macros TEXT)''')

        self.conn.commit()
    def create_table_compliance(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS compliance(
                            centreon_hstid TEXT,
                            centreon_hstname TEXT,
                            centreon_svcname TEXT,
                            snow_id TEXT,
                            snow_alert,
                            snow_schedule
                            snow_maco)''')

        self.conn.commit()

        
    def create_table_compliance_related_ci(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS compliance_related_ci(
                            centreon_hstid TEXT,
                            centreon_hstname TEXT,
                            snow_id TEXT,
                            snow_alert,
                            snow_schedule
                            snow_maco)''')

        self.conn.commit()

    def insert_item(self, centreon_hstid, centreon_svcid,centreon_activate, snow_id, centreon_hstname, centreon_svcname, snow_appstatus, snow_apptype, snow_related_ci, snow_moved, snow_monitor,json_macros):

        query=f'''INSERT INTO diskdrives(
                            centreon_hstid,
                            centreon_svcid,
                            centreon_activate,
                            snow_id,
                            centreon_hstname,
                            centreon_svcname,
                            snow_appstatus,
                            snow_apptype,
                            snow_related_ci,
                            snow_moved,
                            snow_monitor,
                            json_macros) VALUES (
                            "{centreon_hstid}",
                            "{centreon_svcid}",
                            "{centreon_activate}",
                            "{snow_id}",
                            "{centreon_hstname}",
                            "{centreon_svcname}",
                            "{snow_appstatus}",
                            "{snow_apptype}",
                            "{snow_related_ci}",
                            "{snow_moved}",
                            "{snow_monitor}",
                            '{json_macros}')
                        '''

        self.cursor.execute(query)
        self.conn.commit()

    def update_item_dict(self, sys_id, attributes):
        # Construction de la clause SET
        set_clause = ", ".join([f"{key} = ?" for key in attributes.keys()])
        
        # Préparation des valeurs à insérer
        values = list(attributes.values())
        values.append(sys_id)  # Ajout du sys_id pour la clause WHERE

        # Requête SQL sécurisée avec placeholders
        query = f"UPDATE diskdrives SET {set_clause} WHERE snow_id = ?"

        try:
            self.cursor.execute(query, values)
            self.conn.commit()
            print(f"[bold green]Mise à jour réussie pour snow_id = {sys_id}")
        except Exception as e:
            print(f"[bold red]Erreur lors de la mise à jour : {e}")


    def update_item(self, centreon_hstid, centreon_svcid,centreon_activate, snow_id, centreon_hstname, centreon_svcname, snow_appstatus, snow_apptype, snow_related_ci, snow_moved, snow_monitor,json_macros):
        query=f"""
                            UPDATE diskdrives SET
                            centreon_hstid =  "{centreon_hstid}",
                            centreon_svcid = "{centreon_svcid}",
                            centreon_activate = "{centreon_activate}",
                            snow_id = "{snow_id}",
                            centreon_hstname = "{centreon_hstname}",
                            centreon_svcname = "{centreon_svcname}",
                            snow_appstatus = "{snow_appstatus}",
                            snow_apptype = "{snow_apptype}",
                            snow_related_ci = "{snow_related_ci}",
                            snow_moved =  "{snow_moved}",
                            snow_monitor = "{snow_monitor}",
                            json_macros = '{json_macros}'
                            WHERE centreon_hstid= "{centreon_hstid}" AND  centreon_svcid = "{centreon_svcid}" 
                """

        self.cursor.execute(query)
        self.conn.commit()
        
    def select_fs_by_sysid(self, snow_id):
        query=f"SELECT * FROM diskdrives WHERE snow_id='{snow_id}';"
        self.cursor.execute(query)
        data = self.cursor.fetchone()
        dico_sqlite={}
        dico_sqlite['centreon_hstid']=data[0]
        dico_sqlite['centreon_svcid']=data[1]
        dico_sqlite['centreon_activate']=data[2]
        dico_sqlite['snow_id']=data[3]
        dico_sqlite['centreon_hstname']=data[4]
        dico_sqlite['centreon_svcname']=data[5]
        dico_sqlite['snow_appstatus']=data[6]
        dico_sqlite['snow_apptype']=data[7]
        dico_sqlite['snow_related_ci']=data[8]
        dico_sqlite['snow_moved']=data[9]
        dico_sqlite['snow_monitor']=data[10]
        dico_sqlite['json_macros']=data[11]
        # self.conn.close()
        return dico_sqlite

    def select_all_fs_by_sysid(self, snow_id):
        print(snow_id,f'[yellow]<====')
        query=f"SELECT * FROM diskdrives WHERE snow_id='{snow_id}';"
        self.cursor.execute(query)
        data = self.cursor.fetchall()
        return data      


 
    def select_fs(self):
        query=f"SELECT * FROM diskdrives ;"
        self.cursor.execute(query)
        data = self.cursor.fetchall()
        return data

    def delete_item(self, id):
        self.cursor.execute("DELETE FROM diskdrives WHERE id=?", (id,))
        self.conn.commit()

    def check_item_exists(self, centreon_hstid, centreon_svcid):
        self.cursor.execute(f"SELECT * FROM diskdrives WHERE centreon_hstid={centreon_hstid} and centreon_svcid={centreon_svcid}")
        data = self.cursor.fetchone()
        return data is not None

    def close_connection(self):
        self.conn.close()