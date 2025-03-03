from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.core.mail import  get_connection



"""------------------------------ SINGLE EMAIL SENDING ---------------------------------------------"""
class SendEmails:
    
    def __init__(self, *args, **kwargs):
        pass
    
    
    def sendTemplateEmail(self, subject, request, context, template, email_host, user_email):
        sending_status = False
        try:
            context = context
            image = request.build_absolute_uri("/")
            context['image']    = str(image)+'media/images/logo/logo.png'
            # context['twitter']  = str(image)+'media/images/social_media_icons/twitter.png'
            # context['facebook'] = str(image)+'media/images/social_media_icons/facebook.png'
            # context['linkedin'] = str(image)+'media/images/social_media_icons/linkedin.png'
            html_content = render_to_string(str(template), {'context':context})
            text_content = strip_tags(html_content)
            send_e = EmailMultiAlternatives(str(subject), text_content, email_host, [str(user_email)] )
            send_e.attach_alternative(html_content, "text/html")
            send_e.send()

            sending_status = True
        except Exception as es:
            pass
        
        return sending_status



"""------------------------------ BULK EMAIL SENDING ---------------------------------------------"""


class SendBulkEmailsSend:
    
    def __init__(self, *args, **kwargs):
        pass
    def sendBulkEmailSend(self, subject, request, context, template, email_host, user_email):
        sending_status = False
        try:
            connection  = get_connection()
            connection.open()
            context = context
	
            image = request.build_absolute_uri("/")
            context['image']    = str(image)+'media/images/logo/logo.png'
            # context['twitter']  = str(image)+'media/images/social_media_icons/twitter.png'
            # context['facebook'] = str(image)+'media/images/social_media_icons/facebook.png'
            # context['linkedin'] = str(image)+'media/images/social_media_icons/linkedin.png'
            
            html_content = render_to_string(str(template), {'context':context})
            text_content = strip_tags(html_content)
            send_e = EmailMultiAlternatives(str(subject), text_content, email_host, user_email ,connection=connection)
            send_e.attach_alternative(html_content, "text/html")
            send_e.send()
            connection.close()
            sending_status = True
        except Exception as es:
            pass
        
        return sending_status

