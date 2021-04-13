from celery import shared_task
#from django.core.mail import send_mail


'''@shared_task
def send_email_reg(user):
    send_mail(
        'Successful registration',
        f'Thank u {user.username} for having passed registration',
        'anton@gmail.com',
        [f'{user.email}'],
        fail_silently=False
    )
'''