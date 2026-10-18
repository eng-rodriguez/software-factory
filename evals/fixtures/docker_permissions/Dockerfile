FROM python:3.12-slim
RUN useradd --uid 10001 --create-home app
WORKDIR /app
COPY app.py /app/app.py
RUN mkdir /app/data
USER 10001
CMD ["python", "/app/app.py"]
