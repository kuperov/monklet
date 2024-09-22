from django.db import models


class Enquiry(models.Model):
    """Email enquiry from a web visitor."""

    email = models.EmailField(max_length=254, null=False, blank=False)
    name = models.CharField(max_length=254, null=False, blank=False)
    message = models.TextField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Web enquiry"
        verbose_name_plural = "Web enquiries"

    def __str__(self):
        return f"{self.name} <{self.email}>"
