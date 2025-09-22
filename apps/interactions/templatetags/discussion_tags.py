# =================================================================
# apps/interactions/templatetags/discussion_tags.py
# -----------------------------------------------------------------
# MIGRATION: The `get_discussions_for_lesson` tag now accepts a
# lesson's primary key and filters DiscussionThread using the
# relational ForeignKey.
# =================================================================

from django import template
from ..models import DiscussionThread
from ..forms import DiscussionThreadForm, DiscussionPostForm

register = template.Library()

@register.simple_tag
def get_discussions_for_lesson(lesson_pk):
    """ Template tag to fetch all discussion threads for a given lesson_pk. """
    return DiscussionThread.objects.filter(lesson_id=lesson_pk).order_by('-created_at').select_related('student')

@register.simple_tag
def get_discussion_form():
    """ Template tag to provide an instance of the discussion form. """
    return DiscussionThreadForm()

@register.simple_tag
def get_post_form():
    """
    Template tag to provide an instance of the post (reply) form.
    This is used in the thread detail partial.
    """
    return DiscussionPostForm()