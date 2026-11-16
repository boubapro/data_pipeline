FROM python:3.11-slim

RUN apt-get update && apt-get install -y git && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    python -m pip install --upgrade pip

WORKDIR /project
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

COPY run_dbt.sh /usr/local/bin/run_dbt.sh
RUN chmod +x /usr/local/bin/run_dbt.sh

CMD ["/usr/local/bin/run_dbt.sh"]
