from obspy.clients.seedlink.easyseedlink import EasySeedLinkClient
from kafka import KafkaProducer
import json
import time
import concurrent.futures
import threading


# Subclass the client class
class SeedlinkClient(EasySeedLinkClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.producer = KafkaProducer(
            # bootstrap_servers='kafka:9092',
            bootstrap_servers=['kafka1:9092', 'kafka2:9093', 'kafka3:9094'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda v: json.dumps(v).encode('utf-8'),
        )
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=108)

        self.data_station_channel = {}

    def down_sampling(self, trace):
        # jika bukan 20hz, down sampling to 20 Hz
        if trace.stats.sampling_rate > 20:
            before_sampling_rate = trace.stats.sampling_rate
            # decimate to 20 Hz
            # trace.decimate(factor=int(trace.stats.sampling_rate/20), strict_length=False)

            # filter to 20 Hz
            # trace.filter('lowpass', freq=20, corners=2, zerophase=True)

            # resample to 20 Hz
            # trace.resample(sampling_rate=20)

            # interpolate to 20 Hz
            trace.interpolate(sampling_rate=20)
            after_sampling_rate = trace.stats.sampling_rate
            print(f"Down sampling {trace.stats.station}\t{trace.stats.channel} : {before_sampling_rate} -> {after_sampling_rate}")
        return trace

    def log_data(self, data, type="LOG", stat="-"):
        print(f"[+] <{stat}> <{type}>  {data}")

    def on_send_success(self, record_metadata):
        # self.log_data(stat="Kafka", type="Topic", data=f"{record_metadata.topic}")
        # self.log_data(stat="Kafka", type="Partition", data=f"{record_metadata.partition}")
        # self.log_data(stat="Kafka", type="Offset", data=f"{record_metadata.offset}")
        # print(f"Topic: {record_metadata.topic}, Partition: {record_metadata.partition}, Offset: {record_metadata.offset}")
        pass

    def on_send_error(self, excp):  
        print(f"I am an errback {excp}")

    def calculate_gap_time(self, trace):
        key = f"{trace.stats.station}-{trace.stats.channel}"
        if key in self.data_station_channel:
            gap = trace.stats.starttime - self.data_station_channel[key].stats.endtime
            if gap > trace.stats.delta*2:
                # print(f"Gap {trace.stats.station}\t{trace.stats.channel} : {gap}")
                print(f"[{trace.stats.station}-{trace.stats.channel}]\tDelta: {trace.stats.delta}\tGap : {gap}\tDelay : {time.time() - trace.stats.endtime.timestamp}")
            self.data_station_channel[key] = trace
        else:
            self.data_station_channel[key] = trace

    def send_to_kafka(self, trace):
        if time.time() - trace.stats.endtime.timestamp > 60:
            return
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
            'data_provider_time': time.time(),
            'data': trace.data.tolist()
        }
        self.producer.send('trace_topic', data, key=f"{data['station']}-{data['channel']}").add_callback(self.on_send_success).add_errback(self.on_send_error)
        self.producer.flush()

        if trace.stats.channel.endswith('Z'):
            self.producer.send('p_wave_topic', data, key=f"{data['station']}-{data['channel']}").add_callback(self.on_send_success).add_errback(self.on_send_error)
            self.producer.flush()

        # self.producer.flush()


        # self.producer.send('trace_topic', data, key=f"{data['station']}-{data['channel']}").add_callback(self.on_send_success).add_errback(self.on_send_error)
        print(f"Delay {data['station']}\t{data['channel']} : {time.time() - trace.stats.endtime.timestamp}")
        data = None

    def on_data(self, trace):
        # self.executor.submit(self.send_to_kafka, trace)
        # self.executor.submit(self.calculate_gap_time, trace)
        threading.Thread(target=self.send_to_kafka, args=(trace,)).start()
        # threading.Thread(target=self.calculate_gap_time, args=(trace,)).start()

    def on_seedlink_error(self):
        print('Seedlink error')

    def on_terminate(self):
        print('Terminating')

def run_client(server, station_configs, process_id):

    client = SeedlinkClient(server)
    for config in station_configs:
        client.select_stream(config['network'], config['station'], config['seedname'])
    print('Run client', process_id, 'with', len(station_configs), 'station configs finished')
    client.run()