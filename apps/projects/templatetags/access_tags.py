from django import template


register = template.Library()


@register.tag(name="can_edit")
def do_can_edit(parser, token):
    """
    Usage:
    {% can_edit %}
        <content to render if project.can_edit(user) is true>
    {% endcan_edit %}
    """
    # Parse the content between the tags
    nodelist = parser.parse(("endcan_edit",))
    parser.delete_first_token()
    return CanEditNode(nodelist)


class CanEditNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        # Ensure 'project' and 'user' are in the context
        project = context.get("project", None)
        user = context.get("user", None)

        if (
            project
            and user
            and hasattr(project, "can_edit")
            and callable(project.can_edit)
        ):
            # Render the content only if project.can_edit(user) is True
            if project.can_edit(user):
                return self.nodelist.render(context)

        # If condition fails, render nothing
        return ""
