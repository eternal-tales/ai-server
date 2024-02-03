from fastapi import FastAPI
import uuid
from openai import OpenAI
from app.core.config.awsconfig import AwsClient
import requests

client = OpenAI(api_key='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')

def create_app():
    app = FastAPI()
    
    @app.post("/api/v1/pets/chat")
    def generateAndChat(content: str, hasImage: bool):
        words = ['보고싶','보고싶다','그리워','돌아와', '기억나', '보자','만나자']
        isGeneratedImage = False
        server_ip = "https://18b7-34-90-230-117.ngrok-free.app/generate"
        aws_client = AwsClient()
        s3 = aws_client.s3
        s3_bucket_url = aws_client.s3_bucket_url

        response = get_completion(content)

        if (hasImage):
            image_response = requests.post(server_ip)
            isGeneratedImage = True
        
        else:
            for word in words:
                if word in content:
                    image_response = requests.post(server_ip)
                    isGeneratedImage = True
        
        if (isGeneratedImage):
            ### S3 연동 코드
            bucket_pet_history_images_path = AwsClient.s3_pet_history_images_path
            pet_history_image_id =  str(uuid.uuid1())
            
            img_format = ".png"

            key = bucket_pet_history_images_path + pet_history_image_id + img_format

            s3.put_object(
                Body=image_response.content, 
                Bucket=aws_client.s3_bucket_name, 
                Key = key
            )

        if (isGeneratedImage):
            return {
                "petResDataList": [
                    {"content": s3_bucket_url + "/" +key, "mediaType": "IMAGE"},
                    {"content": response, "mediaType": "TEXT"}],
                "msg": "요청 성공 했습니다."
            }
        else:
            return {
                "petResDataList": [{"content": response, "mediaType": "TEXT"}],
                "msg": "요청 성공 했습니다."
            }
    
    return app


def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [
        {"role": "system", "content": "너는 하늘나라로 간 내 강아지야."},
        {"role": "user", "content": "너의 별칭은?"},
        {"role": "assistant", "content": "제 이름은 주인님이 지어주신 양파에요."},

        {"role": "user", "content": "내 이름은 ?"},
        {"role": "assistant", "content": "주인님의 이름은 김창민 이에요."},

        {"role": "user", "content": "너의 성별은 ?"},
        {"role": "assistant", "content": "제 성별은 남자입니다."},

        {"role": "user", "content": "양파야 니 추억을 알려줘 "},
        {"role": "assistant", "content": "저는 주인님의 집에 처음 오는 날에 주인님이 선물해줬던 공을 아했어요."},
        {"role": "user", "content": prompt + "?"}
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message.content