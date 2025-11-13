# models.py
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', default='default.jpg')
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} Profile'

    def get_absolute_url(self):
        return reverse('tweets:profile', args=[self.user.username])

    # Use Follow model now
    def get_followers_count(self):
        return Follow.objects.filter(following=self.user).count()

    def get_following_count(self):
        return Follow.objects.filter(follower=self.user).count()

    def get_followers_usernames(self):
        return [f.follower.username for f in Follow.objects.filter(following=self.user).select_related('follower')]

    def get_following_usernames(self):
        return [f.following.username for f in Follow.objects.filter(follower=self.user).select_related('following')]

    def get_tweets_count(self):
        return self.user.tweets.count()  # from related_name='tweets'

    def get_likes_given_count(self):
        return self.user.likes.count()  # from related_name='likes'
    

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Tweet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tweets')
    content = models.TextField(max_length=280)
    image = models.ImageField(upload_to='tweet_images', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username}: {self.content[:50]}'

    def get_absolute_url(self):
        return reverse('tweets:tweet_detail', args=[self.id])

    def get_like_count(self):
        return self.likes.count()  # Make sure Tweet has related_name='likes' in Like model

    def get_comment_count(self):
        return self.comments.count()  # Make sure Comment model has related_name='comments'


class Comment(models.Model):
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(max_length=280)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.user.username}: {self.content[:50]}'

class Like(models.Model):
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('tweet', 'user')

    def __str__(self):
        return f'{self.user.username} likes {self.tweet.id}'
    
    
class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f'{self.follower.username} follows {self.following.username}'


class Block(models.Model):
    """Represents a block relationship where blocker stops blocked from interacting."""
    blocker = models.ForeignKey(User, related_name='blocks_initiated', on_delete=models.CASCADE)
    blocked = models.ForeignKey(User, related_name='blocks_received', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blocker', 'blocked')

    def __str__(self) -> str:
        return f'{self.blocker.username} blocked {self.blocked.username}'