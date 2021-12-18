FROM ubuntu:latest

ENV container docker
ENV LC_ALL C
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
	postgresql-12 \
	python3 \
	python3-pip \
	systemd \
	systemd-sysv \
	net-tools \
	git

RUN pip3 install pyyaml

RUN echo "listen_addresses = '*'" >> /etc/postgresql/12/main/postgresql.conf
RUN echo "host    all             all             0.0.0.0/0               md5" >> /etc/postgresql/12/main/pg_hba.conf
RUN echo "host    replication     all             0.0.0.0/0               md5" >> /etc/postgresql/12/main/pg_hba.conf

RUN localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8

COPY . .

RUN git clone https://github.com/SadeghHayeri/pgkit.git
RUN cd pgkit && pip install .

CMD ["/lib/systemd/systemd"]