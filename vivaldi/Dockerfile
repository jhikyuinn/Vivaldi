
FROM python:3
WORKDIR /app

COPY constants.py .
COPY vivaldi.py .

#apt 명령어의 설정에 유효 기간을 체크하는 동작을 하지 않도록 설정
RUN echo "Acquire::Check-Valid-Until \"false\";\nAcquire::Check-Date \"false\";" | cat > /etc/apt/apt.conf.d/10no--check-valid-until
RUN apt-get update && apt-get install -y iputils-ping && apt-get install -y net-tools
RUN python3 -m pip install my_package
RUN python3 -m pip install numpy
RUN python3 -m pip install scapy

CMD ["python3" ,"./vivaldi"]
ENTRYPOINT ["python3","vivaldi.py"]

