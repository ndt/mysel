FROM ubuntu:22.04

# Basis Setup
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    wpasupplicant \
    freeradius-utils \
    eapoltest

# Setze Working Directory
WORKDIR /tests

# Kopiere zuerst nur requirements und installiere sie
COPY requirements.test.txt .
RUN pip3 install -r requirements.test.txt

# Kopiere Testdateien
COPY . .

# Setze PYTHONPATH und korrigiere Berechtigungen
ENV PYTHONPATH=/tests
RUN chmod +x -R .

CMD ["pytest", "-v", "--import-mode=importlib"]