from rest_framework.views import APIView
from rest_framework.response import Response

class DiaryCareAPIView(APIView):
    def post(self, request):
        input_text = request.data.get('text', '')
        # AWS Bedrock 호출
        output_text = ''
        return Response({'output_text': output_text})