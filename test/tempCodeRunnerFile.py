# get 5 minutes data from influxdb
end_time = int(time.time() * 1e9)
start_time = int((time.time() - 300) * 1e9)
tables = readInfluxDB('BBJI', 'BHZ', start_time, end_time)
print(tables)