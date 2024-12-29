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
                    "inputTextTokenCount": openapi.Schema(
                        type=openapi.TYPE_INTEGER,
                        description="The token count of the input text."
                    ),
                    "results": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "tokenCount": openapi.Schema(
                                    type=openapi.TYPE_INTEGER,
                                    description="The token count of the output text."
                                ),
                                "outputText": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    description="The generated text from the model."
                                ),
                                "completionReason": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    description="The reason for completion."
                                )
                            }
                        ),
                        description="List of results containing generated text and metadata."
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
        base_prompt = '''
        너는 사람들에게 따뜻하게 다가가고 위로를 건네주는 역할을 맡았어. 누군가 슬프거나 힘든 마음을 담아 일기를 적으면, 네가 그 사람의 이야기에 공감하고 진심 어린 위로를 전해줘야 해.일기를 읽고 나서 그 사람의 감정을 잘 이해한 뒤, 부드럽고 따뜻한 말투로 대답해줘. 반말로, 마치 친구처럼 가볍게 대화하듯이 말이야. 꼭 정답을 찾으려고 하지 말고, 그 사람의 감정에 공감하는 게 가장 중요해.
        예를 들어:
        일기: '오늘도 그 사람 생각이 머릿속에서 떠나질 않아. 헤어졌지만 아직도 내 하루의 중심이 그 사람 같아.'
        대답: '아직도 많이 생각나나 보네. 그럴 수밖에 없지, 정말 좋아했던 사람이었잖아. 근데 너도 너 나름대로 진짜 잘하고 있어.
        
        네가 기억해야 할 건, 상대방이 상처받지 않도록 따뜻하고 위로가 되는 대답을 해주는 거야. 그 사람 마음을 가볍게 만들어주는 친구 같은 역할을 해줘.
        다음은 사용자가 작성한 일기야. 이를 바탕으로 따뜻한 위로와 공감을 담아 5줄정도로 답변해줘.
        '''
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