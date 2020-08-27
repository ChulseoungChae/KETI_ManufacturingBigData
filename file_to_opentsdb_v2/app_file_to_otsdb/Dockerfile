FROM python:2.7
WORKDIR /app
ADD . /app

RUN apt-get update
RUN pip install -r requirements.txt
RUN apt-get install -y net-tools 
RUN apt-get install -y vim 
RUN apt-get install -y openssh-server
RUN echo "PermitRootLogin yes" >> /etc/ssh/sshd_config
RUN echo 'root:root' |chpasswd
RUN pip install flask
#RUN service ssh start

WORKDIR /app/FILE2TSDB
#RUN chmod 755 ./start.sh
CMD ["python","flask_test.py"]
