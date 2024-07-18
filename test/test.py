from obspy.clients.seedlink.easyseedlink import EasySeedLinkClient
import json

# Subclass the client class
class SeedlinkClient(EasySeedLinkClient):
    def on_data(self, trace):
        print('Received trace:')
        print(trace.stats)
        data = {
            'network': trace.stats.network,
            'station': trace.stats.station,
            'location': trace.stats.location,
            'channel': trace.stats.channel,
            'start_time': trace.stats.starttime.timestamp,
            'end_time': trace.stats.endtime.timestamp,
            'sampling_rate': trace.stats.sampling_rate,
            'delta': trace.stats.delta,
            'npts': trace.stats.npts,
            'calib': trace.stats.calib,
            'data_quality': trace.stats.dataquality,
            'num_samples': trace.stats.numsamples,
            'sample_cnt': trace.stats.samplecnt,
            'sample_type': trace.stats.sampletype,
            'data': trace.data.tolist()
        }
        print(data)

    def handle_trace(self, trace):
        print('Received trace:')
        print(trace)

def run_client(server, station_configs, process_id):
    client = SeedlinkClient(server)
    for config in station_configs:
        client.select_stream(config['network'], config['station'], config['seedname'])
    print('Run client', process_id, 'with', len(station_configs), 'station configs finished')
    client.run()

def get_station_configs(station_path, num_seednames=6000):
    with open(station_path, 'r') as file:
        stations = json.load(file)

    station_configs = []
    countSeednames = 0
    isStopped = False
    for station in stations:
        for seedname in station['seednames']:
            station_configs.append({
                'network': station['network'],
                'station': station['station_name'],
                'seedname': seedname
            })
            countSeednames += 1

            if countSeednames == num_seednames:
                isStopped = True
                break

        if isStopped:
            break

    return station_configs

if __name__ == '__main__':
    server = 'geofon.gfz-potsdam.de:18000'

    # station_configs = get_station_configs('./test/stations.json', 10)
    station_configs = [{
        'network': 'GE',
        'station': 'BBJI',
        'seedname': 'BHZ'
    }]
    print(station_configs)

    run_client(server, station_configs, 0)