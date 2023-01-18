FROM python:latest

# Create app directory
RUN mkdir -p /usr/src/app/
WORKDIR /usr/src/app

COPY . .
# Install app dependencies
RUN pip install -r requirements.txt

EXPOSE 8087

CMD python ./conversationbot.py