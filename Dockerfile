FROM python:3.10.9

RUN pip install pipenv

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /auto_market_emu

COPY Pipfile Pipfile.lock /auto_market_emu/

RUN pipenv install --dev --system --deploy --ignore-pipfile

COPY ame_project /auto_market_emu/

