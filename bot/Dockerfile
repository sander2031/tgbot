FROM python:3.9-alpine
WORKDIR /app
COPY . .
RUN apk add postgresql-libs libpq-dev gcc postgresql-dev
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python", "bot.py"]
