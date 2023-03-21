FROM python:3

WORKDIR /opt/door

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

CMD ["tail", "-f", "LICENSE"]
