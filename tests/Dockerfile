FROM python:3.12-slim

# Setze Working Directory
WORKDIR /tests

# Kopiere zuerst nur requirements und installiere sie
COPY requirements.test.txt .
RUN pip install -r requirements.test.txt

# Kopiere Testdateien
COPY . .

# Setze PYTHONPATH und korrigiere Berechtigungen
ENV PYTHONPATH=/tests
RUN chmod +x -R .

CMD ["pytest", "-v", "--import-mode=importlib"]