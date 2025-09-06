from django.db import models

class User(models.Model):
    name=models.CharField(max_length=100)
    email=models.CharField(max_length=100)
    address=models.CharField(max_length=100)
    phone=models.CharField(max_length=100)
    link=models.CharField(max_length=100)
    git=models.CharField(max_length=100)
    edu=models.CharField(max_length=100)
    exp=models.CharField(max_length=100)
    obj=models.CharField(max_length=200)
    skills=models.CharField(max_length=200)
    imge = models.ImageField(upload_to='', default='photos/default.jpg', blank=True, null=True)


    def __str__(self):
        return self.name
    

    
    

