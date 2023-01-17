FROM python:3.10-slim

#Copy all files in current directory into app directory
COPY . /app

#Change Working Directory to app directory
WORKDIR /app

# Install Requirements
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "openfire_sync.py",]