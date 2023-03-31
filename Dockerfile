FROM python:3.10.9

RUN pip install pipenv

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /auto_market

COPY Pipfile Pipfile.lock /auto_market/

RUN pipenv install --dev --system --deploy --ignore-pipfile

COPY project /auto_market/

COPY ./entrypoint.sh /
COPY ./worker-entrypoint.sh /
COPY ./beat-entrypoint.sh /

RUN chmod +x /entrypoint.sh
RUN chmod +x /worker-entrypoint.sh
RUN chmod +x /beat-entrypoint.sh
