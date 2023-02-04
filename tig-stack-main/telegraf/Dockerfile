FROM telegraf:latest

# Create app directory
#RUN mkdir -p /usr/src/app/
WORKDIR /etc/telegraf

RUN apt-get update && \
    apt install -y python3 \
    python3-pip

COPY . .
# Install app dependencies
RUN pip3 install -r requirements.txt
   
# RUN pip install influxdb-client && \
#     pip install pandas && \
#     pip install DateTime && \
#     pip install plotly && \
#     pip install prophet && \
#     pip install ipython

EXPOSE 8080