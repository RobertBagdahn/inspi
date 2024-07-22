from django.db import models


class Faq(models.Model):
    question = models.CharField(max_length=200)
    answer = models.TextField()
    order = models.IntegerField()
    

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question
