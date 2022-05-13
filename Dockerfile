FROM 3.8.13-bullseye

COPY ./requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

EXPOSE 8000 

COPY . . 

CMD ["gunicorn", "server:app", "-w", "4", "-p", "8000"]