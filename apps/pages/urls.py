from django.urls import path
from .views import PagesView, landing_page, comingsoon, enquiry_success


urlpatterns = [
    # temporary - remove when launched
    path("", comingsoon, name="index"),
    path("thanks/", enquiry_success, name="enquiry_success"),
    # /temporary
    path(
        "error/",
        PagesView.as_view(template_name="pages_misc_error.html"),
        name="pages-misc-error",
    ),
    path(
        "under_maintenance/",
        PagesView.as_view(template_name="pages_misc_under_maintenance.html"),
        name="pages-misc-under-maintenance",
    ),
    path(
        "not_authorized/",
        PagesView.as_view(template_name="pages_misc_not_authorized.html"),
        name="pages-misc-not-authorized",
    ),
    path("landing/", landing_page, name="landing"),
    path(
        "pricing/",
        PagesView.as_view(template_name="pricing_page.html"),
        name="pricing-page",
    ),
    path(
        "payment/",
        PagesView.as_view(template_name="payment_page.html"),
        name="payment-page",
    ),
    path(
        "checkout/",
        PagesView.as_view(template_name="checkout_page.html"),
        name="checkout-page",
    ),
    path(
        "help/",
        PagesView.as_view(template_name="help_center_landing.html"),
        name="help-center-landing",
    ),
    path(
        "help/article/",
        PagesView.as_view(template_name="help_center_article.html"),
        name="help-center-article",
    ),
]
