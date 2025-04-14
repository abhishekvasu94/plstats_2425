import psycopg2
import pandas as pd
import json

class FootballDB:

    def __init__(self, db_params):

        self.conn = psycopg2.connect(**db_params)

    def read_from_db(self, query):

        cursor = self.conn.cursor()

        out = cursor.execute(query)

        rows = cursor.fetchall()

        column_names = [desc[0] for desc in cursor.description]

        df = pd.DataFrame(rows, columns = column_names)

        return df

def download_from_s3(client, bucket_name, file_key):

    response = client.get_object(
            Bucket=bucket_name,
            Key=file_key
            )

    file_content = response["Body"].read().decode("utf-8")

    json_content = json.loads(file_content)

    return json_content
