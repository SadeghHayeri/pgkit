ARG OS=ubuntu
ARG OS_VERSION=22.04

FROM ${OS}:${OS_VERSION}

ENV container docker
ENV LC_ALL C
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
	curl \
	python3 \
	python3-pip \
	systemd \
	systemd-sysv \
	net-tools \
	git \
	lsb-core
RUN echo "deb https://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list
RUN curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
ARG POSTGRES_VERSION=13
RUN apt-get update && apt-get install -y postgresql-${POSTGRES_VERSION}

RUN pip3 install pyyaml

RUN echo "listen_addresses = '*'" >> /etc/postgresql/12/main/postgresql.conf
RUN echo "host    all             all             0.0.0.0/0               md5" >> /etc/postgresql/12/main/pg_hba.conf
RUN echo "host    replication     all             0.0.0.0/0               md5" >> /etc/postgresql/12/main/pg_hba.conf

RUN localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8

COPY . .

RUN git clone https://github.com/SadeghHayeri/pgkit.git
RUN cd pgkit && pip install .

CMD ["/lib/systemd/systemd"]
