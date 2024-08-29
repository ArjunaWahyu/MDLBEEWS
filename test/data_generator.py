import time

# throughput 125 data points per second
throughput = 250

# time to sleep between each data point
sleep_time = 1/throughput

start_time = time.time()
for i in range(500):
    start_run_time = time.time()
    print(i)
    end_run_time = time.time()
    time.sleep(sleep_time - (end_run_time - start_run_time))

end_time = time.time()

print(f"Time taken: {end_time - start_time} seconds")