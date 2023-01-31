FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN cat requirements.txt | xargs -n 1 pip install; exit 0

RUN chmod -R -f 777 /app
RUN pip install pyjwt

COPY . .

USER 1000

EXPOSE 8080

#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8300"]
ENTRYPOINT gunicorn --bind :8080 --workers 2 main:app -k uvicorn.workers.UvicornWorker \
    --threads=2 --preload --timeout 60 --worker-tmp-dir /dev/shm --log-level debug