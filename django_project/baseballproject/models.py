from django.db import models

CONTEST_CHOICES = (
    ('fanduel','FANDUEL'),
    ('draftkings', 'DRAFTKINGS'),
    ('yahoo','YAHOO'),
)

class Document(models.Model):
    timeStamp = '%H%M%S'
    location = 'documents/'+timeStamp
    docfile = models.FileField(upload_to=location)
    contest = models.CharField(max_length=10, choices=CONTEST_CHOICES, default='FANDUEL')

    class Meta:
        db_table = "contestInfo"