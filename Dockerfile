FROM 

COPY ./requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt 

RUN apt-get update

EXPOSE 5000 

COPY . . 

CMD []