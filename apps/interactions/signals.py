# =================================================================
# apps/interactions/signals.py
# -----------------------------------------------------------------
# MIGRATION: The webhook payload now correctly accesses related
# object IDs using `instance.student.id`, `instance.course.id`, etc.,
# which is the standard for relational ForeignKey fields.
# =================================================================

import requests
import os
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import DiscussionThread

logger = logging.getLogger(__name__)

@receiver(post_save, sender=DiscussionThread)
def trigger_new_question_webhook(sender, instance, created, **kwargs):
    if created:
        webhook_url = os.getenv('N8N_QUESTION_POSTED_WEBHOOK_URL')

        if not webhook_url:
            logger.warning("N8N_QUESTION_POSTED_WEBHOOK_URL is not set. Skipping webhook.")
            return

        try:
            payload = {
                'thread_id': str(instance.pk),
                'student_id': str(instance.student.pk),
                'student_name': instance.student.full_name or instance.student.username,
                'course_id': str(instance.course.pk),
                'lesson_id': str(instance.lesson.pk),
                'question_title': instance.title,
                'question_text': instance.question,
                'timestamp': instance.created_at.isoformat(),
            }

            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info(f"Successfully sent 'new question' webhook for thread ID {instance.pk}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send 'new question' webhook for thread ID {instance.pk}: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred while sending webhook for thread ID {instance.pk}: {e}")