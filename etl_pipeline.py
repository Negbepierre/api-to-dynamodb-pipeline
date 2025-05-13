import requests
import boto3
import uuid

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('GithubRepos')

# Step 1: Extract from GitHub API
def extract():
    response = requests.get('https://api.github.com/orgs/aws/repos')
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("GitHub API failed")

# Step 2: Transform data
def transform(repos):
    return [
        {
            "id": str(uuid.uuid4()),  # unique ID
            "name": repo["name"],
            "url": repo["html_url"],
            "language": repo["language"] or "Unknown",
        }
        for repo in repos
    ]

# Step 3: Load into DynamoDB
def load(data):
    for item in data:
        table.put_item(Item=item)
    print(f"Loaded {len(data)} items into DynamoDB")

def run_pipeline():
    raw_data = extract()
    transformed = transform(raw_data)
    load(transformed)

if __name__ == "__main__":
    run_pipeline()

