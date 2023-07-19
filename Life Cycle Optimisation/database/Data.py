import sqlite3

import pandas as pd

db = sqlite3.connect("database/data.sqlite")


class Data:

    @staticmethod
    def get_process():
        query = "SELECT ID, Name,Country as Location FROM p_location"
        return pd.read_sql_query(query, db)

    @staticmethod
    def get_flow_for_process(process_id):
        query = "SELECT Flow, amount FROM tbl_lci WHERE process = '" + process_id + "'"
        return pd.read_sql_query(query, db)

    @staticmethod
    def get_impact_methods():
        query = "SELECT ID, Name FROM TBL_IMPACT_METHODS"
        result = db.cursor().execute(query).fetchall()
        methods = []
        for _, row in enumerate(result):
            id = str(row[0])
            name = str(row[1])
            if "(obsolete)" not in name:
                methods.append((id, name))
        return methods

    @staticmethod
    def get_impact_categories(method):
        categories = []
        for i, methodName in method:
            query = "SELECT ID, Name FROM TBL_IMPACT_CATEGORIES "
            query += "WHERE ImpactMethod = '" + str(i) + "'"
            results = db.cursor().execute(query).fetchall()
            for _, row in enumerate(results):
                j = row[0]
                name = methodName + ": " + row[1]
                categories.append((j, name))
        return categories

    @staticmethod
    def get_impact_factor(impact_id, flow_id):
        query = "SELECT Value FROM TBL_IMPACT_FACTORS "
        query += "WHERE ImpactCategory = '" + impact_id + "' AND "
        query += "Flow = '" + flow_id + "'"
        results = db.cursor().execute(query).fetchall()
        if len(results) >= 1:
            return results[0][0]
        return 0

    @staticmethod
    def get_impact_flows(impact_id):
        query = "SELECT Flow FROM TBL_IMPACT_FACTORS "
        query += "WHERE ImpactCategory = '" + impact_id + "'"
        results = db.cursor().execute(query).fetchall()
        for i, result in enumerate(results):
            results[i] = result[0]
        return results

    @staticmethod
    def get_flow():
        query = "SELECT ID AS ID, Flow AS Flow FROM tbl_flows"
        return pd.read_sql_query(query, db)
