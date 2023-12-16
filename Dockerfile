FROM python:3.10

RUN mkdir /dns_server

WORKDIR /dns_server

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY /app /dns_server/app

CMD ["python", "-m", "app"]