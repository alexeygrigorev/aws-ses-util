import os
import yaml

CONFIG_FILE = os.getenv('CONFIG_FILE', 'config.yaml')

with open(CONFIG_FILE, 'rt') as f_in:
    config = yaml.safe_load(f_in) 

aws = config['aws']
aws_region = aws['region']

email = config['email']
email_charset = email['charset']