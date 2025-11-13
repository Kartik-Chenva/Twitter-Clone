from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
from django.shortcuts import render
from .models import Profile, Tweet, Comment, Like, Follow

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_username', 'get_email', 'get_tweet_count', 'get_followers_count', 'get_following_count', 'date_joined')
    search_fields = ('user__username', 'user__email')
    list_filter = ('date_joined',)

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

    def get_tweet_count(self, obj):
        return obj.user.tweets.count()  # ✅ use related_name='tweets'
    get_tweet_count.short_description = 'Tweets'


    def get_followers_count(self, obj):
        return Follow.objects.filter(following=obj.user).count()
    get_followers_count.short_description = 'Followers'

    def get_following_count(self, obj):
        return Follow.objects.filter(follower=obj.user).count()
    get_following_count.short_description = 'Following'

@admin.register(Tweet)
class TweetAdmin(admin.ModelAdmin):
    list_display = ('user', 'content', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'content')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'tweet', 'content', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'content')

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'tweet', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username',)

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('follower__username', 'following__username')

# Custom User Admin to show more user information
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_password_info', 'is_staff', 'is_active', 'date_joined', 'last_login')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)

    def get_password_info(self, obj):
        """Display password hash information"""
        password_hash = obj.password
        if password_hash:
            # Extract algorithm and show first part of hash
            parts = password_hash.split('$')
            if len(parts) >= 3:
                algorithm = parts[0]
                iterations = parts[1] if len(parts) > 1 else 'N/A'
                hash_preview = parts[2][:10] + '...' if len(parts) > 2 else 'N/A'
                return f"{algorithm} ({iterations} iterations) {hash_preview}"
            else:
                return password_hash[:20] + '...'
        return 'No password set'
    get_password_info.short_description = 'Password Hash Info'

    # Add password field to the detail view
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Password Security Information', {
            'fields': ('password_display',),
            'description': 'Password is stored as a cryptographic hash for security. Original passwords cannot be retrieved.'
        }),
    )

    readonly_fields = BaseUserAdmin.readonly_fields + ('password_display',)

    def password_display(self, obj):
        """Display full password hash in detail view"""
        if obj.password:
            return f"{obj.password}\n\n⚠️ SECURITY NOTE: This is an encrypted hash. The original password cannot be recovered from this value."
        return 'No password set'
    password_display.short_description = 'Encrypted Password Hash'

# Unregister the default User admin and register our custom one
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass
admin.site.register(User, CustomUserAdmin)
