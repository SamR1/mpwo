from fittrackee_api import dramatiq, email_service


@dramatiq.actor(queue_name='fittrackee_emails')
def reset_password_email(user, email_data):
    email_service.send(
        template='password_reset_request',
        lang=user['language'],
        recipient=user['email'],
        data=email_data,
    )
