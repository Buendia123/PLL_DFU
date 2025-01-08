import datetime

import pymssql

server = 'SUZ-VM-SQL-002'
database = 'ACCCableTest_DEV'
table = 'FWUpgrade'
user = 'acccable'
password = 'K6$7uAuegP'
conn = pymssql.connect(server, user, password, database)
cursor = conn.cursor()
sn = 'abcd123'
result = 'OK'
Date = datetime.datetime.now()
# CAST('2022-01-01 00:00:00' AS datetime)
sqltask = f"INSERT INTO {table} (SN, Result,Date) VALUES ('{sn}', '{result}','{Date}')"
cursor.execute(sqltask)
conn.commit()
