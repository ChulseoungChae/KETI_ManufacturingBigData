FROM python:3.8
WORKDIR /app
ADD . /app

RUN apt-get update
RUN pip3 install -r requirements.txt
RUN apt-get install -y net-tools 
RUN apt-get install -y vim 
RUN apt-get install -y openssh-server
RUN echo "PermitRootLogin yes" >> /etc/ssh/sshd_config
RUN echo 'root:root' |chpasswd

WORKDIR /app/machine_analysis/

CMD [ "python3", "manufacturing_analysis.py"]