FROM python:3.11-slim

RUN python -m pip install --no-cache-dir --upgrade pip \
    && useradd --create-home --uid 10001 dbt

WORKDIR /project
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=dbt:dbt . .
RUN chmod +x run_dbt.sh && chown dbt:dbt /project

USER dbt

# run_dbt.sh se place dans son propre dossier (/project) : il ne doit pas être
# copié ailleurs, sinon scripts/ et le projet dbt sont introuvables.
CMD ["bash", "/project/run_dbt.sh"]
