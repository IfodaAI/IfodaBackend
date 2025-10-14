from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from django.http import HttpRequest
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Room, Message
from .serializer import RoomSerializer, MessageSerializer
# from products.serializers import DiseaseSerializer

class RoomViewSet(ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes=[IsAuthenticated]

    def create(self, request:HttpRequest|Request, *args, **kwargs):
        data=request.data.copy()
        data["owner"]=request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def get_queryset(self):
        user = self.request.user

        # If user's role is admin, send all orders
        if user.is_superuser or user.role == "ADMIN":
            return Room.objects.all()

        # If it's normal user, send only only their own orders.
        return Room.objects.filter(owner=user)

class MessageViewSet(ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes=[IsAuthenticated]

    def create(self, request: HttpRequest | Request, *args, **kwargs):
        data = request.data.copy()
        data["sender"] = request.user.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save()

        channel_layer = get_channel_layer()
        room = message.room

        payload = {
            "id": str(message.id),
            "role": message.role,
            "sender": str(message.sender.id),
            "status": message.status,
            "content_type": message.content_type,
        }

        if message.content_type == "IMAGE":
            payload["image"] = request.build_absolute_uri(message.image.url) if message.image else ""
        elif message.content_type == "TEXT":
            payload["text"] = message.text
        elif message.content_type == "PRODUCT":
            payload["diseases"] = [{"name":d.name,"description":d.description} for d in message.diseases.all()]
            payload["products"] = [str(p.id) for p in message.products.all()]

        if room:
            async_to_sync(channel_layer.group_send)(
                f'chat_{room.id}',
                {"type": "chat_message", "message": payload},
            )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

# @csrf_exempt  # Only if you need to bypass CSRF protection
# def ai_model_prediction(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         order_id = data.get('order_id')
#         order=Order.objects.get(id=order_id)
#         last_message = order.messages.last()
        
#         # Extract just the path from the URL
#         image_url = str(last_message.image_url)
#         parsed_url = urlparse(image_url)
#         relative_path  = parsed_url.path

#         # Remove the /media/ prefix if it exists (since MEDIA_ROOT already includes this)
#         if relative_path.startswith('/media/'):
#             relative_path = relative_path[7:]  # Remove '/media/'
        
#         # Combine with MEDIA_ROOT to get the full system path
#         full_image_path = os.path.join(django_settings.MEDIA_ROOT, relative_path)
#         response=generate_prompt(full_image_path)
#         if response:
#             disease=Diseases.objects.filter(name__contains=response).first()
#             # pill_ids listiga UUID lar string formatida saqlanadi
#             pill_ids = [str(uuid_obj) for uuid_obj in disease.pills.values_list('id', flat=True)]
#             return JsonResponse({
#                 'success': True,
#                 'pills': pill_ids,
#                 'diseases': [disease.id],  # Optional
#                 'order_id':order_id,
#                 "response":response
#             })
#         # diseases = list(Diseases.objects.values_list("id", "name", "description"))
#         # formatted_diseases = [f"{str(disease_id)}:{name}.{description}" for disease_id, name, description in diseases]
#         # diseases=list(Diseases.objects.values("id", "name", "description"))
        
#         # Here you would call your AI model with the order information
#         # This is a placeholder for your actual AI logic
#         # Replace with your actual implementation
        
#         # Example response with pill IDs
#         pill_ids = [1, 3, 5]  # Replace with your actual AI-predicted pill IDs
#         disease_ids = [2, 4]  # Optional: disease IDs if your API returns these
        
#         return JsonResponse({
#             'success': True,
#             # 'pills': pill_ids,
#             'diseases': disease_ids,  # Optional
#             'order_id':order_id,
#             "response":response
#         })
    
#     return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)