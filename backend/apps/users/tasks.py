from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from .models import User


@shared_task()
def get_users_count():
    """A pointless Celery task to demonstrate usage."""
    return User.objects.count()


@shared_task(bind=True, max_retries=3)
def send_activation_email(self, user_id, activation_link):
    """
    Celery task to send activation email in background.
    
    Args:
        user_id: ID of the user to send activation email
        activation_link: Full activation URL for frontend
    """
    try:
        user = User.objects.get(pk=user_id)
        
        subject = "Activate your account - AllNutrition"
        
        # Context for templates
        context = {
            "user": user,
            "activation_link": activation_link,
            "first_name": user.first_name,
        }
        
        # Render both HTML and plain text versions
        html_content = render_to_string("users/activation_email.html", context)
        text_content = render_to_string("users/activation_email.txt", context)
        
        # Send email with both HTML and plain text versions
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        
        return f"Activation email sent successfully to {user.email}"
        
    except User.DoesNotExist:
        raise Exception(f"User with ID {user_id} does not exist")
    except Exception as exc:
        # Retry the task up to 3 times with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
