FROM python:3.9-buster

WORKDIR /home/metrics
COPY . /home/metrics

RUN python3 -m pip install -r requirements.txt

EXPOSE 9002

CMD ["python3", "buienradar.py"]
