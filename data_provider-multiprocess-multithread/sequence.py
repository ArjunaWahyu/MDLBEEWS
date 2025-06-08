from utils.util import get_station_configs
from SeedlinkClient import run_client

def main(server='geofon.gfz-potsdam.de:18000', station_path = 'data_provider/data/stations.json', num_processes=24, num_station_configs=6000):
    station_configs = get_station_configs(station_path, num_station_configs)

    print('Running with', len(station_configs), 'station configs')
    print('Running with', num_processes, 'processes')

    print('All processes started')

    run_client(server, station_configs, 0)