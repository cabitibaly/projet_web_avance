from django.db.models.signals import post_save
from django.conf import settings
from django.dispatch import receiver
from .models import Otp
from django.core.mail import send_mail
from django.utils import timezone

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_OTP(sender, instance, created, **kwargs):
    if created:
        if instance.role != 'teacher':
            if instance.is_superuser:
                pass
            else:
                Otp.objects.create(user=instance, expire_at=timezone.now() + timezone.timedelta(minutes=5))
                # Otp.objects.create(user=instance, expire_at=timezone.now() + timezone.timedelta(minutes=5))
                instance.is_active = False
                instance.save()
            
            otp = Otp.objects.filter(user=instance).last()

            subject = 'Email verification'
            message = f"""
                        Hi {instance.username}, here is your OTP {otp.code}
                        It expires in 5 minutes, use the url below to redirect back to the website
                        Http://127.0.0.1:8000/verify-email/{instance.id}
                    """
            sender = 'bitibalyclementalex@gmail.com'
            receiver = [instance.email,]

            send_mail(subject, message, sender, receiver, fail_silently=False)