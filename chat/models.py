from django.db import models


class User(models.Model):
    user_id = models.CharField(max_length=25, primary_key=True)
    username = models.CharField(max_length=25)
    email = models.CharField(max_length=100)
    last_active_date = models.DateTimeField()
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "user id: %s; username: %s" % (self.user_id, self.username)


class Message(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=25)
    name = models.CharField(max_length=25)
    content = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "user id: %s; name: %s; content: %s" % (self.user_id, self.name, self.content)
