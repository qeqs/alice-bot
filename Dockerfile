FROM python:2.7.14

WORKDIR /app
COPY . /app

EXPOSE 5000

RUN pip install -r requirements.txt
CMD FLASK_APP=alice_bot/alice_bot.py flask run --host="::"