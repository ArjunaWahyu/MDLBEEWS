from obspy.clients.seedlink.easyseedlink import EasySeedLinkClient
import xml.etree.ElementTree as ET
import json

# # Subclass the client class
# class MyClient(EasySeedLinkClient):
#     # Implement the on_data callback
#     def on_data(self, trace):
#         print('Received trace:')
#         print(trace)

# # Connect to a SeedLink server
# client = MyClient('geofon.gfz-potsdam.de:18000')

# # Retrieve INFO:STREAMS
# streams_xml = client.get_info('STREAMS')

# # Write streams_xml to a .txt file
# with open('streams.txt', 'w') as file:
#     file.write(streams_xml)

# print("streams.xml has been written to streams.txt")

# # open the file in read mode
# with open('streams.txt', 'r') as file:
#     xml_data = file.read()
# # Parse the XML data
# root = ET.fromstring(xml_data)

# stations = []
# for station in root.findall('station'):
#     station_info = {
#         'station_name': station.get('name'),
#         'network': station.get('network'),
#         'description': station.get('description'),
#         'seednames': [stream.get('seedname') for stream in station.findall('stream')]
#     }
#     stations.append(station_info)

# # Write to JSON file
# with open('stations.json', 'w') as json_file:
#     json.dump(stations, json_file, indent=4)

# print("stations.json has been written.")

# ====================================================================================================

# Subclass the client class
class MyClient(EasySeedLinkClient):
    # Implement the on_data callback
    def on_data(self, trace):
        print('Received trace:')
        print(trace)

# Connect to a SeedLink server
client = MyClient('172.19.3.87:18000')

# Retrieve INFO:STREAMS
streams_xml = client.get_info('STREAMS')

# Write streams_xml to a .txt file
with open('streams-IA.txt', 'w') as file:
    file.write(streams_xml)

print("streams.xml has been written to streams-IA.txt")

# # open the file in read mode
# with open('streams.txt', 'r') as file:
#     xml_data = file.read()
# # Parse the XML data
# root = ET.fromstring(xml_data)

# stations = []
# for station in root.findall('station'):
#     station_info = {
#         'station_name': station.get('name'),
#         'network': station.get('network'),
#         'description': station.get('description'),
#         'seednames': [stream.get('seedname') for stream in station.findall('stream')]
#     }
#     stations.append(station_info)

# # Write to JSON file
# with open('stations-IA.json', 'w') as json_file:
#     json.dump(stations, json_file, indent=4)

# print("stations-IA.json has been written.")


# ====================================================================================================

# # open the file in read mode
# with open('stations.json', 'r') as file:
#     stations = json.load(file)

# count = 0
# countChannels = 0
# # print the stations
# for station in stations:
#     if not station['seednames']:
#         continue

#     station['seednames'].sort()

#     print("="*50)
#     print("Station:\t", station['station_name'])
#     print("Network:\t", station['network'])
#     print("Description:\t", station['description'])
#     print("Seednames:\t", station['seednames'])

#     count += 1
#     countChannels += len(station['seednames'])

# print("="*50)
# print("Total number of stations: ", count)
# print("Total number of channels: ", countChannels)