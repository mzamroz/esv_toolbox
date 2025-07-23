FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN \
    apt update && apt install -y unixodbc unixodbc-dev curl gpg && apt clean all && \
    apt install nano -y &&\
    useradd -u 1000 appadmin &&\
    chown -R 1000:1000 /app &&\
    chmod 760 -R /app &&\
    curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg && \
    curl https://packages.microsoft.com/config/debian/12/prod.list | tee /etc/apt/sources.list.d/mssql-release.list && \
    apt update && \
    ACCEPT_EULA=Y apt install -y msodbcsql18

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501 1434

ENV PYTHONPATH=/app

CMD ["streamlit", "run", "./main.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
