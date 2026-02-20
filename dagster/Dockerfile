FROM python:3.11-slim

WORKDIR /app

RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host pypi.python.org dagster dagster-webserver psycopg2-binary

COPY . .

EXPOSE 3000

CMD ["dagster", "dev", "-h", "0.0.0.0", "-p", "3000", "-m", "etl_project"]