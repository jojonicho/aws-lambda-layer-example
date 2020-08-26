from selenium import webdriver
import os
import time
import json
import boto3
import base64
from botocore.exceptions import ClientError
from selenium.webdriver.chrome.options import Options


class OnboardProvider:
    def __init__(self):
        pass

    def delay(self, second):
        time.sleep(second)

    def smart_delay(self, func, max_timeout=20):
        iteration = 0
        while iteration <= 20:
            try:
                if func():
                    break
            except:
                pass
            self.delay(1)
            iteration += 1
        self.delay(2)

    def setup_driver(self):
        options = Options()
        options.binary_location = "/opt/python/bin/headless-chromium"
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1280x1696")
        options.add_argument("--disable-application-cache")
        options.add_argument("--disable-infobars")
        options.add_argument("--no-sandbox")
        options.add_argument("--hide-scrollbars")
        options.add_argument("--enable-logging")
        options.add_argument("--log-level=0")
        options.add_argument("--single-process")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--homedir=/tmp")
        driver = webdriver.Chrome(
            "/opt/python/bin/chromedriver", chrome_options=options
        )
        return driver

    def send_email(self, service, URL, requester, recipient):
        SENDER = "jonathan.nicholas@mekari.com"
        AWS_REGION = "ap-southeast-1"
        client = boto3.client("ses", region_name=AWS_REGION)

        # CONFIGURATION_SET = "ConfigSet"

        # The subject line for the email.
        SUBJECT = f"{service} Access Granting - {requester}"
        # The full path to the file that will be attached to the email.
        # ATTACHMENT = "path/to/customers-to-contact.xlsx"

        # The email body for recipients with non-HTML email clients.
        BODY_TEXT = (
            "Hello,\r\nPlease see the attached file for a list of customers to contact."
        )

        # The HTML body of the email.
        BODY_HTML = f"""\
        <html>
        <head></head>
        <body>
        <p>Hello, please approve the requested service by clicking the link below and add my email {requester}\n{URL}.</p>
        </body>
        </html>
        """

        # The character encoding for the email.
        CHARSET = "utf-8"
        try:
            response = client.send_email(
                Destination={"ToAddresses": [recipient,],},
                Message={
                    "Body": {
                        "Html": {"Charset": CHARSET, "Data": BODY_HTML,},
                        "Text": {"Charset": CHARSET, "Data": BODY_TEXT,},
                    },
                    "Subject": {"Charset": CHARSET, "Data": SUBJECT,},
                },
                Source=SENDER,
            )
        except ClientError as e:
            print(e)
            print(e.response["Error"]["Message"])
        else:
            print("Email sent! Message ID:"),
            print(response["MessageId"])

    def get_secret(self):
        print("getting secret")
        secret_name = "mekari-access-management/manager-credentials"
        region_name = "ap-southeast-1"
        if secret_name == "" or region_name == "":
            raise Exception("Must include SECRET_NAME and REGION_NAME environment")
        # Create a Secrets Manager client
        session = boto3.session.Session()
        client = session.client(service_name="secretsmanager", region_name=region_name)
        try:
            get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        except ClientError as e:
            print(e)
            if e.response["Error"]["Code"] == "DecryptionFailureException":
                raise e
            elif e.response["Error"]["Code"] == "InternalServiceErrorException":
                raise e
            elif e.response["Error"]["Code"] == "InvalidParameterException":
                raise e
            elif e.response["Error"]["Code"] == "InvalidRequestException":
                raise e
            elif e.response["Error"]["Code"] == "ResourceNotFoundException":
                raise e
            else:
                raise e
        else:
            if "SecretString" in get_secret_value_response:
                return get_secret_value_response["SecretString"]
            else:
                return base64.b64decode(get_secret_value_response["SecretBinary"])
