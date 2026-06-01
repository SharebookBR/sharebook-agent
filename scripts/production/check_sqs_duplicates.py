import paramiko
import json
import boto3
from collections import Counter

# SSH para pegar credenciais SQS do container
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('212.85.23.202', port=22, username='root', password='ecoECO4321@@@', timeout=15)

cmd = "docker inspect sharebook-api"
stdin, stdout, stderr = client.exec_command(cmd)
inspect_json = stdout.read().decode()
client.close()

data = json.loads(inspect_json)
env_vars = data[0]['Config']['Env']

sqs_env = {}
for e in env_vars:
    if '=' in e:
        key, _, val = e.partition('=')
        if 'SQS' in key.upper() or ('AWS' in key.upper() and 'S3' not in key.upper()):
            sqs_env[key] = val

aws_access_key = sqs_env.get('AwsSqsSettings__AccessKey')
aws_secret_key = sqs_env.get('AwsSqsSettings__SecretKey')
raw_region = sqs_env.get('AwsSqsSettings__Region', '')
queue_base_url = sqs_env.get('AwsSqsSettings__QueueBaseUrl', '')
low_priority_queue = sqs_env.get('AwsSqsSettings__SendEmailLowPriorityQueue', 'send-email-low-priority')
queue_url = f"{queue_base_url}/{low_priority_queue}"

# Mapear enum .NET para região AWS padrão
region_map = {
    'SAEast1': 'sa-east-1',
    'USEast1': 'us-east-1',
    'USWest2': 'us-west-2',
    'EUWest1': 'eu-west-1',
}
aws_region = region_map.get(raw_region, raw_region)

print(f"Region: {aws_region}")
print(f"Queue URL: {queue_url}")
print()

sqs = boto3.client(
    'sqs',
    region_name=aws_region,
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key
)

attrs = sqs.get_queue_attributes(
    QueueUrl=queue_url,
    AttributeNames=['ApproximateNumberOfMessages', 'ApproximateNumberOfMessagesNotVisible']
)
visible = int(attrs['Attributes']['ApproximateNumberOfMessages'])
in_flight = int(attrs['Attributes']['ApproximateNumberOfMessagesNotVisible'])
print(f"Mensagens na fila: {visible} visíveis, {in_flight} em processamento")
print()

print("Lendo mensagens para checar duplicatas...")
recipients = []
messages_read = 0

while True:
    response = sqs.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=10,
        WaitTimeSeconds=1,
        VisibilityTimeout=30,
        AttributeNames=['All']
    )
    msgs = response.get('Messages', [])
    if not msgs:
        break

    for msg in msgs:
        body = json.loads(msg['Body'])
        for dest in body.get('Destinations', []):
            recipients.append(dest.get('Email', '').lower())
        messages_read += 1

    if messages_read >= 500:
        print("(limite de 500 mensagens lidas)")
        break

print(f"Mensagens lidas: {messages_read}")
print(f"Destinatários totais: {len(recipients)}")

counter = Counter(recipients)
duplicates = {email: count for email, count in counter.items() if count > 1}

if duplicates:
    print(f"\n⚠️  DUPLICATAS ENCONTRADAS: {len(duplicates)} email(s)")
    for email, count in sorted(duplicates.items(), key=lambda x: -x[1])[:20]:
        print(f"  {email}: {count}x")
else:
    print("\n✅ Nenhuma duplicata encontrada nas mensagens lidas.")
