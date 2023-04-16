import sys
import argparse

from pathlib import Path

import yaml
import boto3
import jinja2
import markdown

import pandas as pd
from tqdm.auto import tqdm

import config


ses_client = boto3.client('ses', region_name=config.aws_region)


def send(sender: str, receiver: str, subject: str, html: str, plaintext: str):
    print(f'sending to {receiver}...')

    response = ses_client.send_email(
        Destination={
            'ToAddresses': [receiver],
        },
        Message={
            'Subject': {
                'Charset': config.email_charset,
                'Data': subject,
            },
            'Body': {
                'Html': {
                    'Charset': config.email_charset,
                    'Data': html,
                },
                'Text': {
                    'Charset': config.email_charset,
                    'Data': plaintext,
                },
            },
        },
        Source=sender,
    )
    
    return response


def read(file: Path) -> str:
    with file.open(encoding='utf-8') as f_in:
        return f_in.read()


def read_yaml(file: Path) -> dict:
    with file.open(encoding='utf-8') as f_in:
        return yaml.safe_load(f_in)


def read_template(file: Path) -> jinja2.Template:
    content = read(file)
    return jinja2.Template(content)


def main(template_folder: Path, emails_file: Path):
    styles = read(template_folder / 'style.css')
    email_html_template = read_template(template_folder / 'email.html')
    markdown_template = read_template(template_folder / 'body.md')

    campaign_config = read_yaml(template_folder / 'campaign.yaml')

    sender = campaign_config['email']['sender']
    subject = campaign_config['email']['subject']
    footer = campaign_config['email']['footer']

    df_emails = pd.read_csv(emails_file)
    
    records = df_emails.to_dict(orient='records')

    for record in records:
        receiver = record['email']

        if receiver == 'never.give.up@gmail.com':
            continue

        content_md = markdown_template.render(**record)
        content_html = markdown.markdown(content_md)

        email = email_html_template.render(
            style=styles,
            html_message=content_html,
            footer=footer
        )

        send(sender, receiver, subject, email, content_md)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Send emails with AWS SES')

    parser.add_argument('--template', required=True, help='Folder with the templates')
    parser.add_argument('--emails', required=True, help='Path to CSV with emails')

    args = parser.parse_args()
    template = Path(args.template)
    emails = Path(args.emails)

    main(template, emails)