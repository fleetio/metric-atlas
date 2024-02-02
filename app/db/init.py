import duckdb
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")


@dataclass
class SampleDB:
    file_path: str = "db/sample_data.db"

    def init(self):
        """
        Initialize a local Duck DB instance and load data.
        """
        # Create DB and Schemas
        logging.info("Initializing DB...")
        con = duckdb.connect(self.file_path)
        con.sql("CREATE SCHEMA IF NOT EXISTS core")
        con.sql("CREATE SCHEMA IF NOT EXISTS sales")

        # Macros
        logging.info("Creating Macros...")
        con.sql(
            "CREATE OR REPLACE MACRO DIV0(x, y) AS CASE WHEN y = 0 THEN NULL ELSE x / y END;"
        )
        con.sql(
            "CREATE OR REPLACE MACRO CONVERT_TIMEZONE(timezone, timestamp) AS TIMEZONE(timezone, timestamp);"
        )

        # Load Data
        logging.info("Loading Data...")
        con.sql(
            "CREATE TABLE IF NOT EXISTS sales.opportunities AS FROM read_csv_auto('db/sample_data/opportunities.csv')"
        )
        con.sql(
            "CREATE TABLE IF NOT EXISTS core.calendar AS FROM read_csv_auto('db/sample_data/calendar.csv')"
        )
        con.sql("SELECT * FROM sales.opportunities LIMIT 5").show()
        con.sql("SELECT * FROM core.calendar LIMIT 5").show()


if __name__ == "__main__":
    SampleDB().init()
