from django import template
from email_templates.models import EmailTemplate

register = template.Library()


@register.tag
def email_template(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, template_id = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires a single argument" % token.contents.split()[0])

    return EmailTemplateNode(template_id)


class EmailTemplateNode(template.Node):

    def __init__(self, template_id):
        self.template_id = template_id

    def render(self, context):
        try:
            templ = EmailTemplate.objects.get(pk=self.template_id)
        except EmailTemplate.DoesNotExist:
            raise template.TemplateSyntaxError("%r template does not exists" % self.template_id)
        context[self.template_id] = templ
        return ""
