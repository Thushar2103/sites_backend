from datetime import timedelta
from django.utils import timezone
from django.db import models
import uuid
from django.contrib.auth.models import User

# Create your models here.

# class Users(models.Model):
#     token=models.CharField(max_length=100)
#     username=models.CharField(max_length=100,null=True)
#     email=models.EmailField()
#     password=models.CharField(max_length=100)

    
class SitesFormat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,auto_created=True,unique=True,editable=False)
    title = models.CharField(max_length=255)
    jsoncontent = models.TextField(null=True)
    htmlcontent = models.TextField(null=True)
    date_time=models.DateField(auto_now_add=True)
    private = models.BooleanField(default=False)  # New field
    shared_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title
    

    def is_expired(self):
        if self.shared_at:
            return timezone.now() > self.shared_at + timedelta(hours=1)
        return False
    


