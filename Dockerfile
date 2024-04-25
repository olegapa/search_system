FROM python:3.12

ADD requirements.txt /app/requirements.txt

WORKDIR /app

RUN python -m pip install --upgrade pip && \
    python -m pip install -r /app/requirements.txt

COPY . /app

EXPOSE 5055
ENTRYPOINT [ "bash" , "/app/src/entrypoint.sh" ]