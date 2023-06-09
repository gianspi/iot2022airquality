import os
import socket
import tempfile
temp_dir = tempfile.TemporaryDirectory()
os.environ['MPLCONFIGDIR'] = temp_dir.name
import pandas as pd
from datetime import datetime, timezone
from prophet import Prophet, diagnostics
import requests

import sys

from influxdb_client import InfluxDBClient, Point, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS

import logging
logging.getLogger('prophet').setLevel(logging.WARNING)

logging.basicConfig(

    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO

)

logger = logging.getLogger(__name__)



# import cmdstanpy
# cmdstanpy.install_cmdstan()
# cmdstanpy.install_cmdstan(compiler=True) # only valid on Windows



cmdstanpy_logger = logging.getLogger("cmdstanpy")
cmdstanpy_logger.disabled = True

# cmdstanpy_logger.handlers = []

# cmdstanpy_logger.setLevel(logging.DEBUG)

# handler = logging.FileHandler('all.log')

# handler.setLevel(logging.DEBUG)

# handler.setFormatter(
#     logging.Formatter(
#         '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#         "%H:%M:%S",
#     )
# )

# cmdstanpy_logger.addHandler(handler)


# DA LEVARE PIù AVANTI
from IPython.display import display

token = "LUaijeA_-hxGtLkz9axuiCVt51pgGPakizsI7wESL5QAe0vEbr7z1CUoK42Jj0s8lrKT6UWzDmi32hc9E8g-Tw--"
BUCKET = '"Air_Quality"'
org = "IoT_Team"
client = InfluxDBClient(url="http://influxdb:8086", token=token, debug=False, org=org)
query_api = client.query_api()
# write_api = client.write_api(write_options=SYNCHRONOUS)
# _write_client = client.write_api(write_options=WriteOptions(batch_size=1000, 
#                                                             flush_interval=10_000,
#                                                             jitter_interval=2_000,
#                                                             retry_interval=5_000))


AIR_QUALITY = '"air_quality"'
FORECAST_MEASUREMENT = 'forecast'
#FIELDS = ['hum', 'temp', 'conc', 'aqi', 'rssi']
FIELDS_TO_FORECAST = ['hum', 'temp', 'conc']
#FIELDS_TO_FORECAST = [FIELDS for _ in range(3)]
TAGS = ['sensorID', 'lat', 'lon'] # 'host', 

X = 1

METRIC = 'mse'

NS = 1000000000
#tz = 'Europe/Rome'
MIN_ROWS = 2
COLUMNS_TO_BE_REMOVED = ['result', 'table', '_start', '_stop', '_measurement'] # , 'host', 'aqi', 'rssi'
NEWLINE_TO_BE_REMOVED = ['host', 'aqi', 'rssi']
SENSOR_COLUMNS = ['sensorID', 'lat', 'lon']
SENSOR_ID = 0
LAT = 1
LON = 2

HOST = socket.gethostname()
MEASUREMENT = '_measurement'
TIME = '_time'
PD_TIME = 'ds'
PD_VALUE = 'y'
FORECAST_VALUE = 'yhat'

FREQ = 'S'
#API_KEY_OPENWEATHER = 'c1e149dbf4a6201212455140073ae1d3'
API_KEY_OPENWEATHER = ''
OPENWEATHER_REQUEST = 'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api}&units={unit}'
OUT_TEMP_FIELD = 'out'
UNIT = 'metric'


# VEDERE DI FARE LA QUERY CON UN FIELD SPECIFICO
# def result_to_dataframe(result):
#     raw = []
#     for table in result:
#         for record in table.records:
#             raw.append((record.get_value(), record.get_time()))
#     return pd.DataFrame(raw, columns=['y', 'ds'], index=None)

def query(field) :
        # ' import "timezone" ' \
        #         ' option location = timezone.location(name : "Europe/Rome") ' \
        query = ' from(bucket:' + BUCKET + ') ' \
                ' |> range(start: -1d) ' \
                ' |> filter(fn: (r) => r._measurement == ' + AIR_QUALITY + ') ' \
                ' |> filter(fn: (r) => r._field == "' + field + '") ' \
                ' |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value") '

        # UTILE PER NON FARE I PASSAGGI INTERMEDI
        # result_query = client.query_api().query(query=query)
        # result = result_to_dataframe(result_query)

        result = client.query_api().query_data_frame(query)
        #logging.info(result)
        if len(result.index) > 0 : 
                result = result.rename(columns={TIME : PD_TIME})
                #result = result.drop(columns=['host'])
                # Preparing Dataframe: 
                #df = df.drop(columns=['result', 'table', '_start', '_stop', 'host', '_measurement', 'lat', 'lon', 'sensorID'])
                result = result.drop(columns=COLUMNS_TO_BE_REMOVED)
                #result['ds'] = pd.to_datetime(result['ds']).apply(lambda t : t.replace(tzinfo=None))
                result['ds'] = result['ds'].dt.tz_localize(None)
        else :
                result = None

        #display(result)
        return result


def getIndex(line) :
        start_ix = line.find("index=") + len("index=")
        end_ix = line.find(",", start_ix)
        if end_ix == -1 :
                end_ix = line.rfind(" ")
        end_ix = end_ix - 1
        index = int(line[start_ix:end_ix])
        return index


def getLineLatLon(line) :
        start_lat = line.find("lat=") + len("lat=")
        start_lon = line.find("lon=") + len("lon=")
        end_lat = line.find(",", start_lat)
        end_lon = line.find(",", start_lon)
        lat = float(line[start_lat:end_lat])
        lon = float(line[start_lon:end_lon])
        return lat, lon


def addOutTemp(line, out_temp) :
        last_wp = line.rfind(" ")
        new_line = line[0:last_wp] + "," + OUT_TEMP_FIELD + "=" + str(out_temp) + line[last_wp:]
        return new_line


def printDatetime(line) :
        last_wp = line.rfind(" ")
        t = line[last_wp:]
        t = t[:len(t)-9]
        #logging.info(t[:len(t)-9])
        logging.info("\n")
        logging.info(datetime.fromtimestamp(int(t)))
        logging.info("\n")


def parseNewLine(newline) :
        dictNewLine = {}

        i = newline.find(",")
        measurementL = newline[0:i]
        tfts = newline[i+1:].split(" ")
        tagsL = tfts[0].split(",")
        fieldsL = tfts[1].split(",")
        timestampL = tfts[2]
        lL = []
        for j in range(len(tagsL)) :
                lL.extend(tagsL[j].split("="))
        for j in range(len(fieldsL)) :
                lL.extend(fieldsL[j].split("="))
        lL.extend([PD_TIME, datetime.fromtimestamp(int(timestampL) // NS)])
        
        dictNewLine = dict((lL[i], lL[i+1]) for i in range(0, len(lL), 2))
        dfL = pd.DataFrame([dict((lL[i], lL[i+1]) for i in range(0, len(lL), 2))])
        dfL = dfL.drop(columns=NEWLINE_TO_BE_REMOVED)
        # dfL['ds'] = pd.to_datetime(dfL['ds']).apply(lambda t : t.tz_convert(tz=timezone.utc))
        #dfL[PD_TIME] = pd.to_datetime(dfL[PD_TIME]).apply(lambda t : t.replace(tzinfo=None))
        dfL[PD_TIME] = dfL[PD_TIME].dt.tz_localize(None)
        #display(dfL)

        return dfL


def setTags(df) :
        #display(df)
        tagsStr = ''
        columns = df.columns.tolist()
        if len(columns) > 0 :
                tagsStr = tagsStr + columns[0] + '=' + str(df.at[0, df.columns[0]])

                for i in range(1, len(columns)) :
                        tagsStr = tagsStr + ',' + columns[i] + '=' + str(df.at[0, df.columns[i]])

        return tagsStr

# def setTags(p, df) :
#         for tag in TAGS :
#                 p.tag(tag, str(df.at[0, tag]))
#         return p


def setFields(df) :
        #display(df)
        fieldsStr = ''
        columns = df.columns.tolist()
        if len(columns) > 0 :
                fieldsStr = fieldsStr + columns[0] + '=' + str(df.at[0, df.columns[0]])

                for i in range(1, len(columns)) :
                        fieldsStr = fieldsStr + ',' + columns[i] + '=' + str(df.at[0, df.columns[i]])

        return fieldsStr

# def setFields(p, df) :
#         for field in FIELDS_TO_FORECAST :
#                 p.field(field, float(df.at[0, field]))
#         return p


def dfToInflux(df) :
        # p = Point(df.at[0, MEASUREMENT])
        # p = setTags(p, df[TAGS])
        # p = setFields(p, df[FIELDS_TO_FORECAST])
        # p.measurement(int(df.at[0, TIME].timestamp() * NS))
        return df.at[0, MEASUREMENT] + ',' + setTags(df[TAGS]) + ' ' + setFields(df[FIELDS_TO_FORECAST]) + ' ' + str(int(df.at[0, TIME].timestamp() * NS))


def main() :
        forecasted = True
        #df = query()
        #columns = FIELDS_TO_FORECAST.copy()
        #columns.extend(TIME)
        #forecast = pd.DataFrame(columns=columns)
        forecastDict = dict(_measurement=FORECAST_MEASUREMENT, host=HOST)
        number_freq = 10
        freq = str(number_freq) + FREQ
        #display(df)

        # index = 1
        # ix = 0
        

        for line in sys.stdin :
                # ix = getIndex(line)
                # logging.info("\n")
                # logging.info("newline number: " + str(ix))
                # logging.info("\n")
                # logging.info("cicle number: " + str(index))
                logging.info("\n")
                logging.info(datetime.now())
                
                logging.info("\n")
                logging.info(line)
                forecasted = True
                line = line.rstrip('\n')
                
                line_lat, line_lon = getLineLatLon(line)
                url = OPENWEATHER_REQUEST.format(lat = line_lat, lon = line_lon, api = API_KEY_OPENWEATHER, unit = UNIT)
                
                #logging.info(url)
                try:
                    r = requests.get(url)
                    results = r.json()
                    #logging.info(results)
                    if results['cod'] == 200 :
                        line = addOutTemp(line,  results['main']['temp'])
                        #logging.info(line)
                except Exception:
                    logging.error("Error getting weather")

                printDatetime(line)
                logging.info("\n")
                logging.info(line)
                logging.info("\n")
                print(line)
                sys.stdout.flush()

                # VERIFICARE SE ANCHE DOPO PRINT E FLUSH, I DATI NON VENGONO IMMEDIATAMENTE SALVAT SU INFLUX
                # SE NON VENGONO SALVATI SERVE AGGIUNGERE AL DATAFRAME RITORNATO DALLA QUERY, ANCHE LE RIGHE PRECEDENTI
                # NON DOVREBBE COMPARIRE; QUINDI è DA AGGIUNGERE MANUALMENTE
                # if df is not None :
                #         df = pd.concat([df, parseNewLine(line)], ignore_index=True)
                # else :
                #         df = parseNewLine(line)

                #display(df)

                
                #df = df.rename(columns={"_time" : "ds"}) 
                #df['ds'] = pd.to_datetime(df['ds']).apply(lambda t : t.tz_convert(tz=tz))
                #df['ds'] = pd.to_datetime(df['ds']).apply(lambda t : t.tz_convert(tz=timezone.utc))
                #df['ds'] = pd.to_datetime(df['ds']).apply(lambda t : t.replace(tzinfo=None))
                

                for field in FIELDS_TO_FORECAST :
                        # logging.info("\n")
                        # logging.info("forecast " + field)
                        # logging.info("\n")
                        df = query(field)
                        if (df is None or (df is not None and len(df.index) < MIN_ROWS)) :
                                forecasted = False
                                continue
                        logging.info("\n")
                        logging.info(df.columns)
                        logging.info("\n")

                        forecastDict[SENSOR_COLUMNS[SENSOR_ID]] = df.at[len(df.index) - 1, SENSOR_COLUMNS[SENSOR_ID]]
                        forecastDict[SENSOR_COLUMNS[LAT]] = df.at[len(df.index) - 1, SENSOR_COLUMNS[LAT]]
                        forecastDict[SENSOR_COLUMNS[LON]] = df.at[len(df.index) - 1, SENSOR_COLUMNS[LON]]

                        m = Prophet(yearly_seasonality=False,
                                weekly_seasonality=False,
                                daily_seasonality=30,
                                n_changepoints=35,
                                changepoint_range=1,
                                changepoint_prior_scale=0.01
                                # interval_width=1.0
                                )

                        
                        columns = SENSOR_COLUMNS.copy()
                        df = df.drop(columns=columns)
                        logging.info("\n")
                        logging.info(df.columns)
                        logging.info("\n")
                        #logging.info(df.columns.tolist())
                        df = df.rename(columns={field : PD_VALUE})
                        #logging.info(df.columns.tolist())
                        # fields = FIELDS_TO_FORECAST.copy()
                        # fields.remove(field)
                        # columns.extend(fields)
                        # dfToForecast = df.loc[(df[SENSOR_COLUMNS[SENSOR_ID]] == forecastDict[SENSOR_COLUMNS[SENSOR_ID]]) & (df[SENSOR_COLUMNS[LAT]] == forecastDict[SENSOR_COLUMNS[LAT]]) & (df[SENSOR_COLUMNS[LON]] == forecastDict[SENSOR_COLUMNS[LON]])]
                        # dfToForecast = df.drop(columns=columns)
                        # dfToForecast = dfToForecast.rename(columns={field : PD_VALUE}) #field[1:-1]
                        # #display(dfToForecast)

                        # # DataFrame must have the timestamp column as an index for the client. 
                        # df.set_index("_time")
                        logging.info("\n")
                        logging.info(df)
                        m.fit(df, algorithm='Newton') # m.fit(df)
                        #future = m.make_future_dataframe(periods=X, freq=1, include_history=True)
                        # SE X DIVERSO DA 1 ALLORA PRENDERE PROBABILMENTE SOLO LA PRIMA RIGA
                        future = m.make_future_dataframe(periods=X, freq=freq, include_history=False)
                        # future.tail()
                        tmp = m.predict(future)
                        
                        if PD_TIME not in forecastDict :
                                forecastDict[TIME] = tmp.at[0, PD_TIME] #tmp.iloc[0]['ds']

                        #tmp = tmp.rename(columns={FORECAST_VALUE : field}) # additive_terms , multiplicative_terms , yhat , trend
                        #display(tmp)
                        
                        # FORSE USARE .update()
                        forecastDict[field] = tmp.at[0, FORECAST_VALUE] #field[1:-1]

                        
                #forecast['_measurement'] = FORECAST_MEASUREMENT
                #forecast['sensorID'] = "a57"
                #forecast['_time'] = time # datetime.fromtimestamp(int((df.iloc[len(df.index) - 1]['_time'].timestamp() + 10) * NS) // NS)
                #forecast['_time'] = pd.to_datetime(forecast['_time'])
                if forecasted :

                        forecast = pd.DataFrame([forecastDict])
                        #forecast = forecast.replace(['localhost'], socket.gethostname())
                        #logging.info(forecast.iloc[[0]])
                        forecast_line = dfToInflux(forecast.iloc[[0]])
                        #logging.info(forecast_line)
                        #
                        # display(forecast.iloc[[0]])
                        print(forecast_line)
                        sys.stdout.flush()

                # logging.info("\n")
                # logging.info("end newline number: " + str(ix))
                # logging.info("\n")
                # logging.info("end cicle number: " + str(index))
                # logging.info("\n")
                # ix = ix + 1

                # for i in range(len(forecast.index)) :
                #         #display(forecast.iloc[[i]])
                #         print(dfToInflux(forecast.iloc[[i]]))
                #         sys.stdout.flush() 

                # # _write_client.write(bucket, org, lines)
                # _write_client.write(bucket.name, record=df, data_frame_measurement_name='',
                #                     data_frame_tag_columns=[''])

                # diagnostics.performance_metrics(forecast, metrics=metric, rolling_window=0.1)


if __name__ == '__main__' :
        main()
        logging.info("SIAMO FUORI DAL MAIN, QUALCOSA è ANDATO STORTO !!!!!")
        # _write_client.__del__()
        client.__del__()
        