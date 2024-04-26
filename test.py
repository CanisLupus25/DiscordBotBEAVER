import datetime

print(datetime.datetime(2000, 12, 1, 0, 0, 0) - datetime.datetime(2000, 11, 1, 2, 3, 2) < datetime.timedelta(days=10))