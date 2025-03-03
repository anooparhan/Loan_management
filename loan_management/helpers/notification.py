from apps.notification.serializers import NotificationCreateorUpdateSerializer




# def create_notification(notification_text, employee=None, designation=None, department=None, is_admin=False, request=None):
#     """
#     Common function to create notifications.
#     """

#     notification_data = {
#         "notification_text": notification_text,
#         "employee_id": employee.id if employee else None,  # Ensure it's an ID, not an instance
#         "designation": designation.id if designation else None,
#         "department": department.id if department else None,
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
def create_notification(notification_text, employee=None, designation=None, department=None, is_admin=False, request=None):
    """
    Common function to create notifications.
    """

    notification_data = {
        "notification_text": notification_text,
        "employee_id": employee if isinstance(employee, int) else employee.id if employee else None,
        "designation": designation if isinstance(designation, int) else designation.id if designation else None,
        "department": department if isinstance(department, int) else department.id if department else None,
        "is_admin": is_admin,
    }

    notification_serializer = NotificationCreateorUpdateSerializer(
        data=notification_data, context={"request": request}
    )

    if notification_serializer.is_valid():
        notification_instance = notification_serializer.save()
        print(f"Notification ID {notification_instance.id} created successfully!", flush=True)
    else:
        print("Notification Serializer Errors:", notification_serializer.errors, flush=True)
