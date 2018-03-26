import pyodbc


class db:
    connection = None
    cursor = None

    def __init__(self, server, database, username, password):
        driver = '{ODBC Driver 13 for SQL Server}'

        self.connection = None
        try:
            connectionString = 'DRIVER={};PORT=1433;SERVER={};PORT=1443;DATABASE={};UID={};PWD={}'
            self.connection = pyodbc.connect(connectionString.format(driver, server, database, username, password))
            self.cursor = self.connection.cursor()
            print('Connected to database')
        except (Exception) as e:
            print(e)

    def close(self):
        if self.cursor is not None:
            self.cursor.close()

        if self.connection is not None:
            self.connection.close()

    def commit(self):
        if self.connection is not None:
            self.connection.commit()

    def query_no_return(self, query, parameters = None):
        if parameters is None:
            self.cursor.execute(query)
        else:
            self.cursor.execute(query, parameters)

    def query_many(self, query, parameters):
        if parameters is None:
            self.cursor.execute(query)
        else:
            self.cursor.execute(query, parameters)
        return self.cursor.fetchall()

    def query_one(self, query, parameters):
        if parameters is None:
            self.cursor.execute(query)
        else:
            self.cursor.execute(query, parameters)
        return self.cursor.fetchone()

    def query_dict_return(self, query, parameters):
        if parameters is None:
            self.cursor.execute(query)
        else:
            self.cursor.execute(query, parameters)
        results = {}
        for row in self.cursor.fetchall():
            results[row[0]] = row
        return results

