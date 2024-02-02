import boto3
import yaml

class AwsClient():
    s3_pet_history_images_path = 'assets/eternaltales/images/pethisotrys/'

    def __new__(cls):
        if not hasattr(cls,'instance'):
            print('aws client created')
            cls.instance = super(AwsClient, cls).__new__(cls)

        return cls.instance
    
    def __init__(self):
        file_path = "resources/env/application-aws.yml"
        with open(file_path, 'r') as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
            aws = data['aws']
            bucket = aws['bucket']

        self.s3 = self.s3_connection()
        self.dynamodb = self.dynamodb_connection()
        self.s3_bucket_name = bucket['name']
        self.s3_bucket_url = "https://"+bucket['name']+".s3."+bucket['location']+".amazonaws.com"

    def s3_connection(self,):
        try:
            file_path = "resources/env/application-aws.yml"
            with open(file_path, 'r') as file:
                data = yaml.load(file, Loader=yaml.FullLoader)
                aws = data['aws']
                bucket = aws['bucket']

            s3 = boto3.client(
                service_name="s3",
                region_name=bucket['location'], # 자신이 설정한 bucket region
                aws_access_key_id=aws['access_key_id'],
                aws_secret_access_key=aws['secret_access_key'],
            )

        except Exception as e:
            print(e)

        else:
            print("s3 bucket connected!")
            return s3
        
    def dynamodb_connection(self,):
        try:
            file_path = "resources/env/application-aws.yml"
            with open(file_path, 'r') as file:
                data = yaml.load(file, Loader=yaml.FullLoader)
                aws = data['aws']
                bucket = aws['bucket']

            s3 = boto3.resource(
                service_name="dynamodb",
                region_name=bucket['location'], # 자신이 설정한 bucket region
                aws_access_key_id=aws['access_key_id'],
                aws_secret_access_key=aws['secret_access_key'],
            )

        except Exception as e:
            print(e)

        else:
            print("dynamodb connected!")
            return s3
