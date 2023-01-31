from influxdb_client import InfluxDBClient, Point, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS

# DA LEVARE PIù AVANTI
from IPython.display import display

FIELDS = ['hum', 'temp', 'conc']
AIR_QUALITY = '"air_quality"'
FORECAST_MEASUREMENT = 'forecast'

token = "LUaijeA_-hxGtLkz9axuiCVt51pgGPakizsI7wESL5QAe0vEbr7z1CUoK42Jj0s8lrKT6UWzDmi32hc9E8g-Tw--"
BUCKET = '"Air_Quality"'
org = "IoT_Team"
client = InfluxDBClient(url="http://influxdb:8086",
                        token=token, debug=False, org=org)
query_api = client.query_api()


query = ' from(bucket:' + BUCKET + ') ' \
        ' |> range(start: -15m) ' \
        ' |> filter(fn: (r) => r._measurement == ' + AIR_QUALITY + ') ' \
        ' |> filter(fn: (r) => r["_field"] == "temp" or r["_field"] == "hum" or r["_field"] == "conc")' \
        ' |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value") ' \
        ' |> mean() '

result = client.query_api().query_data_frame(query)

display(result)