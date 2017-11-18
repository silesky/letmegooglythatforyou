FROM python:3.6.3
RUN apt-get update
ADD requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip3 install -r requirements.txt
ADD . /app
EXPOSE 8000
# Start unbuffered output
CMD ["python3", "-u", "app.py"]
