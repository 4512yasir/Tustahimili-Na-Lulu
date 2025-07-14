from app import db
from app.models import Notification
import logging

def send_notification(user_id, title, message):
    try:
        notif = Notification(
            user_id=user_id,
            title=title,
            message=message
        )
        db.session.add(notif)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(f"Failed to send notification to user {user_id}: {e}")
