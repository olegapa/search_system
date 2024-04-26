FROM python:3.12

ADD requirements.txt /bot/requirements.txt

WORKDIR /bot

RUN python -m pip install --upgrade pip && \
    python -m pip install -r /bot/requirements.txt

COPY . /bot

EXPOSE 5055
ENTRYPOINT [ "bash" , "/bot/entrypoint.sh" ]