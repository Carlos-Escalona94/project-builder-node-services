import shutil
import os
import subprocess
import boto3
import botocore
import sys, getopt
from cfn_tools import load_yaml
import cfn_flip.yaml_dumper
from pygit2 import Repository

from pathlib import Path

allowed_branches = ["master"]

aws_default_region = "sa-east-1"

ssm_client = boto3.client('ssm', region_name = aws_default_region)

services_to_deploy = ['accounts']

def main(argv):
    # total arguments
    n = len(argv)

    if(n < 4):
        exit(1) #TODO
    
    opts, args = getopt.getopt(argv, "p:e:", ["projects=","env="])

    input_projects = ''
    env = ''

    for opt, arg in opts:
        if opt in ('-p', '--projects'):
            input_projects = arg
        elif opt in ('-e', '--env'):
            env = arg

    if(input_projects == ''):
        exit(1) #TODO

    if(env == ''):
        exit(1) #TODO

    ########################################################
    repository = Repository('.')
    git_branch = repository.head.shorthand
    
    repository_name = Path(repository.remotes['origin'].url).stem

    if(not git_branch in allowed_branches):
        raise
    
    project_name = ssm_client.get_parameter(Name = "ProjectName")['Parameter']['Value']

    if(not project_name in repository_name):
        raise

    deploy_bucket = ssm_client.get_parameter(Name = "DeployBucket")['Parameter']['Value']
    #########################################################

    s3 = boto3.resource('s3')

    #get affected projects
    projects = input_projects.split(",")
    #projects = filter(filter_projects_by_services, input)
    services = {}

    for x in projects:
        
        split_character = '/'
        if(len(x.split(split_character)) < 2):
            split_character = '-'

        if(len(x.split(split_character)) < 2):
            continue
    
        if(not (x.split(split_character)[0] in services_to_deploy)):
            continue

        print(x)
        service = x.split(split_character)[0]
        
        endpoint = split_character.join(x.split(split_character)[1:])
        if(not service in services):
            services[service] = [endpoint]
        else:
            services[service].append(endpoint)

    for x in services:
        shutil.make_archive(f"{x}", 'zip', f'dist/apps/{x}')

    #trigger deploy pipeline => upload artifacts (for know just run deployments in build project (move artifacts))

    #unzip project
    for x in services:
        shutil.unpack_archive(f'{x}.zip', f'{x}')
        os.remove(f"{x}.zip")

    print(services)
    #dont use services get from folder
    for x in services:
        if 'infra' in services[x]:
            services[x].remove('infra')
            #check if lambda
            
            lambdas = []
            lambdas_resource_types = ["AWS::Serverless::Function"]
            with open(f'{x}/infra/assets/resources.yml') as f:
                raw = f.read()
                data_dict = load_yaml(raw)

                for template_key, template_value in data_dict.items(): #TODO
                    if template_key == 'Resources':
                        for resources_key, resources_value in template_value.items():
                            if ("Type", "AWS::Serverless::Function") in resources_value.items():
                                for lambda_key, lambda_values in resources_value.items():
                                    if lambda_key == "Properties":
                                        for key, values in lambda_values.items():
                                            if(key == "FunctionName"):
                                                lambdas.append(values)

                                
            for y in lambdas:
                try:
                    s3.Object(deploy_bucket, f'dist/{x}/lambdas/{y}.zip').load()
                except botocore.exceptions.ClientError as e:
                    if e.response['Error']['Code'] == '404':
                        #create dummy zip
                        s3.meta.client.upload_file('dummy.zip', deploy_bucket, f'dist/{x}/lambdas/{y}.zip')
                        pass
                    else:
                        raise
                else:
                    print('Exists')
                    pass
            result = subprocess.call(['python', f'{x}/infra/assets/deploy.py', env])
            if(result != 0):
                exit(result)
        
        procs = [subprocess.Popen(['python', f'{x}/{y}/assets/deploy.py', env]) for y in services[x]] #TODO assets?

        for p in procs:
            p.wait()

    
    shutil.rmtree(f'{x}')


if __name__ == "__main__":
    main(sys.argv[1:])