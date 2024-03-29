import logging
from influxdb_client import InfluxDBClient, Point, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS
import warnings
from influxdb_client.client.warnings import MissingPivotFunction

warnings.simplefilter("ignore", MissingPivotFunction)

# DA LEVARE PIù AVANTI
from IPython.display import display

# Enable logging

logging.basicConfig(

    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO

)

logger = logging.getLogger(__name__)

BUCKET = '"Air_Quality"'
FIELDS = ['"temp"', '"hum"', '"conc"']
AIR_QUALITY = '"air_quality"'

token = "LUaijeA_-hxGtLkz9axuiCVt51pgGPakizsI7wESL5QAe0vEbr7z1CUoK42Jj0s8lrKT6UWzDmi32hc9E8g-Tw--"
org = "IoT_Team"
client = InfluxDBClient(url="http://influxdb:8086", token=token, debug=False, org=org)
query_api = client.query_api()

MESSAGE_FORMAT = {FIELDS[0][1:len(FIELDS[0]) - 1]: "Temperature: ", FIELDS[1][1:len(FIELDS[1]) - 1]: "Humidity: ", FIELDS[2][1:len(FIELDS[2]) - 1]: "Gas concentration: "}

minutes = 15

def queryMean():

        #logger.info("Log prova")

        query = ' from(bucket:' + BUCKET + ') ' \
        ' |> range(start: -' + str(minutes) + 'm) ' \
        ' |> filter(fn: (r) => r._measurement == ' + AIR_QUALITY + ') ' \
        ' |> filter(fn: (r) => r._field == ' + FIELDS[0] + ' or r._field == ' + FIELDS[1] + ' or r._field == ' + FIELDS[2] + ') ' \
        ' |> mean() '

        result = client.query_api().query_data_frame(query)
        #result = result.drop(columns = {"result","table","lat","lon","sensorID","_start","host"})

        # logger.info(result.columns.tolist())
        # for col in result.columns:
        #         logger.info(col)

        #logger.info(MESSAGE_FORMAT) 
        message = ""
        if len(result.index) > 0 :
                for i in range(len(FIELDS)) :
                        #logger.info(result.at[i, "_field"])
                        message += "\n" if i > 0 else ""
                        message += MESSAGE_FORMAT[result.at[i, "_field"]] + str(result.at[i, "_value"])
        else :
                message = "There is no data to display in the last " + str(minutes) + " minutes."

        logger.info(message)
        return message