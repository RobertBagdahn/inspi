from django.db import models


class Faq(models.Model):
    question = models.CharField(max_length=200)
    answer = models.TextField()
    sorting = models.IntegerField()

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question


class MessageType(models.Model):
    sorting = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=300, default="")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Message Type"
        verbose_name_plural = "Message Types"


class Message(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(default="")
    name = models.CharField(max_length=50, default="")
    subject = models.CharField(max_length=100, default="")
    body = models.CharField(max_length=500)
    is_processed = models.BooleanField(default=False)
    type = models.ForeignKey(
        MessageType,
        on_delete=models.PROTECT,
    )
    def __str__(self):
        return f"{self.type}: {self.subject[:50]}"

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
