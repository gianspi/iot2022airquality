FROM telegraf:latest

RUN apt-get update && \
    apt install -y python3 \
    python3-pip
   
RUN pip install influxdb-client && \
    pip install pandas && \
    pip install DateTime && \
    pip install plotly && \
    pip install prophet && \
    pip install ipython

EXPOSE 8080

# RUN apt-get update && \
#     apt-get install -yq tzdata && \
#     ln -fs /usr/share/zoneinfo/Europe/Rome /etc/localtime && \
#     dpkg-reconfigure -f noninteractive tzdata

# ENV TZ="Europe/Rome"

# RUN chmod +w /root/.config/matplotlib

# RUN apt-get update && \
#     apt-get install -y software-properties-common && \
#     add-apt-repository -y ppa:deadsnakes/ppa && \
#     apt-get update && \
#     apt install -y python3.12