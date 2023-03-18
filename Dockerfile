FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt /app

RUN pip3 install -r requirements.txt

COPY . /app

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port", "8501", "--logger.level=debug"]