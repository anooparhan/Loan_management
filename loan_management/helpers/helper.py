import datetime
import hashlib
from django.contrib.auth import get_user_model
import json,socket,base64
# from apps.elasticsearch.eu import create_index,insert_one_data,es
# from apps.notification.serializers import NotificationCreateorUpdateSerializer





# def create_notification(notification_text, employee=None, designation=None, department=None, is_admin=False, request=None):
#     """
#     Common function to create notifications.
#     """
#     notification_data = {
#         "notification_text": notification_text,
#         "employee_id": employee,
#         "designation": designation,
#         "department": department,
#         "is_admin": is_admin,
#     }

#     notification_serializer = NotificationCreateorUpdateSerializer(
#         data=notification_data, context={"request": request}
#     )

#     if notification_serializer.is_valid():
#         notification_instance = notification_serializer.save()
#         print(f"Notification ID {notification_instance.id} created successfully!", flush=True)
#     else:
#         print("Notification Serializer Errors:", notification_serializer.errors, flush=True)



def get_token_user_or_none(request):
    User = get_user_model()
    try:
        instance = User.objects.get(id=request.user.id)
    except Exception:
        instance = None
    finally:
        return instance


def get_object_or_none(classmodel, **kwargs):
    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.DoesNotExist:
        return None


def handle_index_error(key, content):
    try:
        return content[key]
    except IndexError:
        return ''
    except:
        return ''
    
    
def handle_none(value):
    try:
        return value if value is not None else ''
    except:
        return ''
    
    


def decode_base64_image(image_base64):
    if not image_base64.startswith('data:image/'):
        raise ValueError("Unsupported image format or missing data prefix")
    
    try:
        metadata, base64_data = image_base64.split(',', 1)
        content_type = metadata.split(';')[0].split(':')[1]
        file_extension = f".{content_type.split('/')[1]}"
    except (IndexError, ValueError):
        raise ValueError("Malformed base64 image string")
    
    try:
        image_data = base64.b64decode(base64_data)
    except base64.binascii.Error:
        raise ValueError("Invalid base64 encoding")
    
    
    return image_data, file_extension, content_type