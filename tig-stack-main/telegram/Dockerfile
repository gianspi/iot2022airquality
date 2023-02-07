FROM python:latest

# Create app directory
RUN mkdir -p /usr/src/app/
WORKDIR /usr/src/app

COPY . .
# Install app dependencies
#RUN pip3 install --upgrade pip3
RUN pip3 install -r requirements.txt
RUN pip3 install python-telegram-bot[job-queue] --pre


EXPOSE 8087

CMD python3 ./timerbot.py