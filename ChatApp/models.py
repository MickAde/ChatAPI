from django.db import models
from django.contrib.auth.models import AbstractUser

# I extended AbstractUser to allow for easy customization of the default Django user model.
# AbstractUser provides all the default fields such as username, email, and password, while allowing us
# to add custom fields, like 'tokens', without altering Django's default behavior.

class User(AbstractUser):  
    tokens = models.IntegerField(default=4000)  # Additional field for managing token balance for the AI chat system.

    class Meta:
        verbose_name = "User"  # A human-readable singular name for the model.
        verbose_name_plural = "Users"  # A human-readable plural name for the model.

    def __str__(self):
        return self.username  # Returns the username when the User object is represented as a string.


class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat by {self.user.username}"  # Returns a readable string representation of the chat.
