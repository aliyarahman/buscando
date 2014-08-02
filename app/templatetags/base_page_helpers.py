from django import template
from app.models import Resource
from app.models import Provider
from django.db import models
from django.template import Library, Node

register = Library()

def get_resources():
	return Resource.objects.all()

class GetLoggedInOrganization(Node):

	def __init__(self, user_id = None):
		self.user_id = user_id

	def render(self, context):
		self.orgs = Provider.objects.filter(admin_id = self.user_id)
		if orgs:
			context['org_name'] = self.orgs[0].name
			context['org_id'] = self.orgs[0].id
		else:
			context['org_name'] = None
			context['org_id'] = None
		return ''

def get_logged_in_organization(parser, token):
	# First break up the arguments that have been passed to the template tag
    bits = token.contents.split()
    if len(bits) != 2:
        raise TemplateSyntaxError, "get_logged_in_organization tag takes exactly 1 argument"
    return GetLoggedInOrganization(bits[1])

register.tag('get_logged_in_organization', get_logged_in_organization)
