import boto3
import time
import json


client = boto3.client("dynamodb")
skip_to_table_name = None

all_table_names = []
with open("table_names.json") as f:
    all_table_names = json.load(f)

if not all_table_names:
    while True:
        table_names = None
        if skip_to_table_name:
            table_names = client.list_tables(
                ExclusiveStartTableName=skip_to_table_name, Limit=100
            )
        else:
            table_names = client.list_tables(Limit=100)

        if not table_names or not table_names["TableNames"]:
            break

        skip_to_table_name = table_names["TableNames"][len(table_names) - 1]
        all_table_names = all_table_names + table_names["TableNames"]
        time.sleep(1)

    with open("table_names.json", "w") as f:
        json.dump(all_table_names, f)

print(all_table_names)
