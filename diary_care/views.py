from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ibyeolnote import settings
import boto3
import json
from botocore.exceptions import ClientError

class DiaryCareAPIView(APIView):
    @swagger_auto_schema(
        operation_summary="텍스트 생성 API",
        operation_description=(
            "This endpoint generates text based on the user's input using the Amazon Bedrock service."
        ),
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "inputText": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="유저의 입력 텍스트",
                )
            },
            required=["inputText"],
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "generated_text": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="The generated text from the model."
                    )
                },
            ),
            500: "Error invoking the model.",
        },
    )
    def post(self, request):
        
        bedrock_client = boto3.client(
            service_name = 'bedrock-runtime',
            region_name = 'us-east-1',
            aws_access_key_id = settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY
        )
        model_id = 'amazon.titan-text-premier-v1:0'
        
        # 프롬프트 엔지니어링
        base_prompt = ''
        # 사용자에게 입력받는 텍스트
        input_text = request.data.get('inputText')
        # 최종 프롬프트
        prompt = f"{base_prompt}\n\nUser Input: {input_text}"
        
        native_request = {
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": 512, # 최대 토큰 수
                "temperature": 0.5, # 창의성 조절
                "topP": 0.9 # 확률 분포의 상위 P 퍼센트
            },
        }

        # Convert the native request to JSON.
        request = json.dumps(native_request)

        try:
            # Invoke the model with the request.
            response = bedrock_client.invoke_model(
                modelId=model_id,
                body=request,
                contentType="application/json"
            )

        except (ClientError, Exception) as e:
            return Response(f"ERROR: Can't invoke '{model_id}'. Reason: {e}", status=500)

        # Decode the response body.
        model_response = json.loads(response["body"].read())
        
        return Response(model_response, status=200)