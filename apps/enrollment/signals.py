# =================================================================
# apps/enrollment/signals.py
# -----------------------------------------------------------------
# MIGRATION: Webhook payload updated to use the relational fields.
# `enrollable_id` is now `object_id` and `enrollable_type` is
# derived from the `content_type` relation.
# =================================================================

import requests
import os
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Enrollment
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Enrollment)
def trigger_new_enrollment_webhook(sender, instance, created, **kwargs):
    if created:
        webhook_url = os.getenv('N8N_ENROLLMENT_CREATED_WEBHOOK_URL')

        if not webhook_url:
            logger.warning("N8N_ENROLLMENT_CREATED_WEBHOOK_URL is not set. Skipping webhook.")
            return

        payload = {
            'enrollment_id': str(instance.pk),
            'student_id': str(instance.student.pk),
            'enrollable_id': str(instance.object_id),
            'enrollable_type': instance.content_type.model, # e.g., 'course' or 'learningpath'
            'enrollment_date': instance.enrollment_date.isoformat(),
        }

        try:
            response = requests.post(webhook_url, json=payload, timeout=5)
            response.raise_for_status()
            logger.info(f"Successfully sent webhook for enrollment ID {instance.pk}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send webhook for enrollment ID {instance.pk}: {e}")