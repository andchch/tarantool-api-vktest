FROM python:3.12-alpine

WORKDIR /app

COPY ./api .

RUN pip install --upgrade pip --no-cache-dir
RUN pip install -r requirements.txt --no-cache-dir

CMD ["fastapi", "run"]