#!/usr/bin/env python3

import time

from lxml import etree
from prometheus_client import Gauge, start_http_server
import requests


def buienradar_current_data():
    data = requests.get('http://data.buienradar.nl/1.0/feed/xml')
    document = etree.fromstring(data.content)
    for station_node in document.xpath('//weerstations/weerstation'):
        int_val = lambda val, default=None: default if val == '-' else int(val)
        float_val = lambda val, default=None: default if val == '-' else float(val)
        yield {
            'name': station_node.xpath('stationnaam/text()')[0],
            'humidity_pct': float_val(station_node.xpath('luchtvochtigheid/text()')[0]),
            'pressure_hpa': float_val(station_node.xpath('luchtdruk/text()')[0]),
            'rain_mmph': float_val(station_node.xpath('regenMMPU/text()')[0], 0),
            'sight_m': float_val(station_node.xpath('zichtmeters/text()')[0]),
            'sunintensity_mw2': float_val(station_node.xpath('zonintensiteitWM2/text()')[0], 0),
            'temperature_c': float_val(station_node.xpath('temperatuurGC/text()')[0]),
            'winddirection_deg': int_val(station_node.xpath('windrichtingGR/text()')[0]),
            'windgust_ms': float_val(station_node.xpath('windstotenMS/text()')[0]),
            'windspeed_bft': int_val(station_node.xpath('windsnelheidBF/text()')[0]),
            'windspeed_ms': float_val(station_node.xpath('windsnelheidMS/text()')[0]),
        }


prometheus_gauges = {
    'humidity_pct': Gauge('buienradar_humidity_pct', 'humidity', ['station']),
    'pressure_hpa': Gauge('buienradar_pressure_hpa', 'The atmospheric pressure in hecto pascal', ['station']),
    'rain_mmph': Gauge('buienradar_rain_mmph', 'The amount of rain in millimeters per hour', ['station']),
    'sight_m': Gauge('buienradar_sight_m', 'The visibility in meters', ['station']),
    'sunintensity_mw2': Gauge('buienradar_sunintensity_mw2', 'The intensity of solar radiation in watts per square meter', ['station']),
    'temperature_c': Gauge('buienradar_temperature_c', 'The temperature in degrees celsius', ['station']),
    'winddirection_deg': Gauge('buienradar_winddirection_deg', 'The wind direction in degrees. 0=north, 90=east, etc', ['station']),
    'windgust_ms': Gauge('buienradar_windgust_ms', 'The speed of wind gusts in meters per second', ['station']),
    'windspeed_bft': Gauge('buienradar_windspeed_bft', 'The wind speed on the Beaufort scale', ['station']),
    'windspeed_ms': Gauge('buienradar_windspeed_ms', 'The wind speed in meters per second', ['station']),
}

def main():
    start_http_server(9002)
    while True:
        for station in buienradar_current_data():
            name = station['name'][len('Meetstation '):]
            for metric in set(station.keys()) - {'name'}:
                value = station[metric]
                if value is not None:
                    prometheus_gauges[metric].labels(station=name).set(value)
        # Buienradar queries the KNMI which refreshes every 10 minutes.
        time.sleep(10 * 60)

main()
