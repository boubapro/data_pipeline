FROM python:3.11-slim

RUN pip install --upgrade pip && \
    pip install dbt-snowflake

WORKDIR /project
COPY . .
RUN dbt deps

COPY run_dbt.sh /usr/local/bin/run_dbt.sh
RUN chmod +x /usr/local/bin/run_dbt.sh

CMD ["/usr/local/bin/run_dbt.sh"]
