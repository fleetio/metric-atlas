from dataclasses import dataclass
import streamlit as st
import snowflake.connector
import duckdb


@dataclass
class Database:
    connection_type: str = "duckdb"
    connection_parameters: dict = None

    def __post_init__(self):
        if self.connection_type == "duckdb":
            self.connection_parameters = st.secrets["duckdb"]

        elif self.connection_type == "snowflake":
            self.connection_parameters = st.secrets["snowflake"]

    @st.cache_resource(show_spinner=False)
    def connection(self):
        if self.connection_type == "duckdb":
            connection = duckdb.connect(self.connection_parameters["path"])

        elif self.connection_type == "snowflake":
            connection = snowflake.connector.connect(
                **self.connection_parameters, client_session_keep_alive=True
            )

        return connection

    @st.cache_data(ttl=600, show_spinner=False)
    def execute_query(self, query, data_frame=True):
        connection = self.connection()

        if self.connection_type == "duckdb":
            if data_frame is True:
                data = connection.sql(query).df()
            else:
                data = connection.sql(query).fetchall()

        elif self.connection_type == "snowflake":
            cur = connection.cursor(snowflake.connector.DictCursor)

            try:
                if data_frame is True:
                    data = cur.execute(query).fetch_pandas_all()
                else:
                    data = cur.execute(query).fetchall()
            finally:
                cur.close()

        return data


if __name__ == "__main__":
    results = Database(connection_type="duckdb").execute_query(
        "SELECT * FROM core.calendar LIMIT 5"
    )
    print(results)
