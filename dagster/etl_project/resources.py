from dagster import ConfigurableResource
from pydantic import Field
import psycopg2

class PostgresResource(ConfigurableResource):
    host: str = Field(description="Postgres host")
    port: int = Field(description="Postgres port", default=5432)
    user: str = Field(description="Postgres user")
    password: str = Field(description="Postgres password")
    database: str = Field(description="Postgres database name")

    def get_connection(self):
        return psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            dbname=self.database
        )

# Define the resource configuration
# In a real app, use EnvVar("POSTGRES_PASSWORD") instead of hardcoding!
db_resource = PostgresResource(
    host="postgres",  # Docker service name
    user="etl_user",
    password="etl_password",
    database="etl_db"
)