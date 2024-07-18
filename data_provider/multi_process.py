from SeedlinkClient import run_client
from utils.util import get_station_configs, get_station_by_network
import multiprocessing
from time import sleep

def main(server='geofon.gfz-potsdam.de:18000', station_path = 'data_provider/data/stations.json', num_processes=24, num_station_configs=6000):
    # station_configs = get_station_configs(station_path, num_station_configs)
    station_configs = get_station_by_network(station_path, ['GE'])

    print('Running with', len(station_configs), 'station configs')
    print('Running with', num_processes, 'processes')

    processes = []
    num_configs = len(station_configs)//num_processes
    for i in range(num_processes):

        p = multiprocessing.Process(target=run_client, args=(server, station_configs[num_configs*i:num_configs*(i+1)], i))
        processes.append(p)

    for p in processes:
        p.start()
        sleep(0.2)

    print('All processes started')