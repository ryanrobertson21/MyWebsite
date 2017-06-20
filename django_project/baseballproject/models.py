from django.db import models

class Document(models.Model):
    timeStamp = '%H%M%S'
    location = 'documents/'+timeStamp
    docfile = models.FileField(upload_to=location)
