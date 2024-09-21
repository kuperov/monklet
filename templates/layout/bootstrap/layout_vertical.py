from web_project.template_helpers.theme import TemplateHelper


class TemplateBootstrapLayoutVertical:
    def init(context):
        context.update(
            {
                "layout": "vertical",
                "content_navbar": True,
                "is_navbar": True,
                "is_menu": True,
                "is_footer": True,
                "navbar_detached": True,
                "navbar_type": "fixed",
                "theme": "theme-semi-dark",
                "style": "system",
                "rtl_support": False,
            }
        )

        # map_context according to updated context values
        TemplateHelper.map_context(context)

        return context
