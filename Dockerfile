FROM python:3.12

COPY requirements.txt /app/
COPY src /app/

WORKDIR /app

RUN python -m pip install --upgrade pip && \
    python -m pip install -r requirements.txt

EXPOSE 5055
ENTRYPOINT [ "bash" , "/app/entrypoint.sh" ]