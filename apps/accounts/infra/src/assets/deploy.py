import subprocess
import sys

if(len(sys.argv) < 2):
    exit(2)

env = sys.argv[1]
# result = subprocess.call(['sam.cmd', 'deploy', '--capabilities', 'CAPABILITY_NAMED_IAM', '--s3-bucket', f'ringer-{env}-deploys', '--s3-prefix', 'whatsapp/stack-channel-integration-whatsapp', '--region', 'sa-east-1', '--stack-name', 'stack-channel-integration-whatsapp', '--parameter-overrides', f'ENV={env}', '--no-fail-on-empty-changeset', '--template', 'whatsapp/infra/assets/serverless.yml'])

exit(0)