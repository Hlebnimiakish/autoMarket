FROM python:3.10.9

RUN pip install pipenv

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /ame

COPY Pipfile Pipfile.lock /ame/

RUN pipenv install --dev --system --deploy --ignore-pipfile

COPY autoMarketEMU /ame/

