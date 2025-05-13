import boto3

dynamodb = boto3.client('dynamodb')

# List of tables you want to delete
tables_to_delete = ["GithubRepos", "EVChargeStations", "FootballCoaches"]

for table_name in tables_to_delete:
    try:
        response = dynamodb.delete_table(TableName=table_name)
        print(f"✅ Deleted table: {table_name}")
    except dynamodb.exceptions.ResourceNotFoundException:
        print(f"❌ Table not found: {table_name}")
    except Exception as e:
        print(f"⚠️ Error deleting {table_name}: {e}")

