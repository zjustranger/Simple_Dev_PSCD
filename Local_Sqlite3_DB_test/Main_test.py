import sqlite3 as st

con = st.connect('DEMO.db')

# con.set_authorizer()

cur = con.cursor()

cur.execute("select * from sqlite_master")

print(cur.fetchall())