FROM python:3.9 

ADD entrypoint.py .
RUN pip install -r requirements.txt
ENTRYPOINT [“python”, “./entrypoint.py”] 