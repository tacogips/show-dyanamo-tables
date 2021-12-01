import boto3
import time
import json
import sys

table_name_filter = None
if len(sys.argv) > 1:
    table_name_filter = sys.argv[1]

all_table_names = []
try:
    with open("table_names.json") as f:
        all_table_names = json.load(f)
except:
    pass

client = boto3.client("dynamodb")
if not all_table_names:
    skip_to_table_name = None
    while True:
        table_names = None
        if skip_to_table_name:
            print(f"skipping to {skip_to_table_name}")
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

    all_table_names = list(set(all_table_names))
    with open("table_names.json", "w") as f:
        json.dump(all_table_names, f)

if table_name_filter:
    all_table_names = [each for each in all_table_names if "devlambda" in each]

all_table_names.sort()
dynamo_resource = boto3.resource("dynamodb")

definitions = []
for e in all_table_names:
    table_resource = dynamo_resource.Table(e)
    keys_or_indices = []
    for attr in table_resource.attribute_definitions:
        keys_or_indices.append(
            {"field": attr["AttributeName"], "type": attr["AttributeType"]}
        )

    fetched_fields = client.scan(TableName=e, Select="ALL_ATTRIBUTES", Limit=1)
    fetched_fields = fetched_fields["Items"]
    fields = []
    for each_item in fetched_fields:
        for (key, value) in each_item.items():
            tpe = None
            for t in value:
                tpe = t
            fields.append({"field_name": key, "type": tpe})

    definition = {
        "table": e,
        "keys_or_indices": keys_or_indices,
        "fields": fields,
        "data_count": table_resource.item_count,
    }

    definitions.append(definition)

with open("table_attrs.json", "w") as f:
    json.dump(definitions, f)
