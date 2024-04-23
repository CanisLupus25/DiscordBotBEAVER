import sqlite3

file = open('statistic.db', mode='w')
dbase = sqlite3.connect(file.name)
dbase.execute()