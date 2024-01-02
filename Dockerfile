FROM python:alpine

RUN apk --no-cache add gcc musl-dev

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip setuptools-scm
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python", "tictactoebot.py"]
