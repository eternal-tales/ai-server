from fastapi import FastAPI
import uuid
from openai import OpenAI
from app.core.config.awsconfig import AwsClient
from app.util.image_util import read_image
from app.util.pil2byte import pil2byte
from PIL import Image

client = OpenAI(api_key='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')

def create_app():
    app = FastAPI()

    @app.get("/api/v1/ai/test")
    def test():
        return {"Hello": "World"}
    
    @app.post("/api/v1/pets/chat")
    def createPetChat(content: str):
        return {
            "petResDataList": [{"content": "나도 보고 싶어...", "mediaType": "TEXT"}],
            "msg": "요청 성공 했습니다."
        }
    
    @app.get("/api/v1/chatgpt/test/{prompt}")
    def testChatGpt(prompt: str):
        response = get_completion(prompt)
        return {"msg":"test 성공"}
    
    @app.get("/api/v1/s3/test")
    def testS3ImagePost():
        img = read_image("resources/assets/test/images/dog_test.jpg")

        img_pil = Image.fromarray(img)
        img_byte_arr = pil2byte(img_pil)

        ### S3 연동 코드
        aws_client = AwsClient()
        s3 = aws_client.s3
        bucket_pet_history_images_path = AwsClient.s3_pet_history_images_path
        pet_history_image_id =  str(uuid.uuid1())
        
        img_format = ".png"

        key = bucket_pet_history_images_path + pet_history_image_id + img_format
        
        s3.put_object(
            Body=img_byte_arr, 
            Bucket=aws_client.s3_bucket_name, 
            Key = key
        )

        return {"msg":"성공"}
    
    return app

def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Who won the world series in 2020?"},
        {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
        {"role": "user", "content": "Where was it played?"},
        {"role": "user", "content": prompt}
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message.content