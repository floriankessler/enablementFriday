FROM python:3.7

# Ensure that the python output is sent straight to terminal (e.g. your
# container log) without being first buffered and that you can see the output
# of your application (e.g. flask logs) in real time.
ENV PYTHONUNBUFFERED 1

# Prevent Python from writing out pyc files
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
