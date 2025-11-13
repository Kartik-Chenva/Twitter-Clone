from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.db.models import Q, Count
from collections import Counter
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
import re

from .models import Profile, Tweet, Comment, Like, Follow, Block
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, TweetForm, CommentForm, AdminProfileEditForm, AdminTweetEditForm, UserEditForm


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

def admin1(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email')
        password = request.POST.get('password')

        # Try to authenticate with username first
        user = authenticate(request, username=username_or_email, password=password)
        
        # If authentication with username fails, try with email
        if user is None:
            # Find user by email safely (avoid MultipleObjectsReturned)
            user_obj = User.objects.filter(email=username_or_email).first()
            if user_obj:
                user = authenticate(request, username=user_obj.username, password=password)

        if user:
            if user.is_staff or user.is_superuser:
                login(request, user)
                return redirect('/custom_admin/')  # Redirect to real Django admin panel
            else:
                messages.error(request, 'Access denied. You are not an admin user.')
        else:
            messages.error(request, 'Invalid username/email or password.')

    return render(request, 'tweets/admin_login.html')



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from tweets.models import Tweet, Comment, Like, Follow, Profile, Block
from django.contrib.auth.models import User, Group

@user_passes_test(lambda u: u.is_staff)
def custom_admin_dashboard(request):
    context = {
        'user': request.user,
        'tweets_count': Tweet.objects.count(),
        'comments_count': Comment.objects.count(),
        'likes_count': Like.objects.count(),
        'follows_count': Follow.objects.count(),
        'profiles_count': Profile.objects.count(),
        'users_count': User.objects.count(),
        'groups_count': Group.objects.count(),
    }
    return render(request, 'tweets/custom_admin.html', context)


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from tweets.models import Tweet

@staff_member_required
def admin_tweets(request):
    # Get unified search query from URL parameters
    search_query = request.GET.get('search_query', '').strip()
    
    # Base queryset
    tweets = Tweet.objects.select_related('user').all()
    
    # Apply search filter if search query exists
    if search_query:
        # Check if the search query looks like a date (YYYY-MM-DD format)
        import re
        date_pattern = r'^\d{4}-\d{2}-\d{2}$'
        
        if re.match(date_pattern, search_query):
            # Search by date
            tweets = tweets.filter(created_at__date=search_query)
        else:
            # Search by username
            tweets = tweets.filter(user__username__icontains=search_query)
    
    # Order by created date (latest first)
    tweets = tweets.order_by('-created_at')
    
    # Paginate (4 tweets per page)
    paginator = Paginator(tweets, 4)
    page_number = request.GET.get('page')
    tweets = paginator.get_page(page_number)
    
    return render(request, 'tweets/admin_tweets.html', {
        'tweets': tweets,
        'search_query': search_query,
    })


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from .models import Comment
from .forms import CommentForm
from django.core.paginator import Paginator

@staff_member_required
def manage_comments(request):
    # Get search query from request
    search_query = request.GET.get('search', '')
    
    # Base queryset
    all_comments = Comment.objects.select_related('user', 'tweet').order_by('-created_at')
    
    # Apply search filter if query exists
    if search_query:
        all_comments = all_comments.filter(
            Q(user__username__icontains=search_query) |
            Q(tweet__content__icontains=search_query) |
            Q(content__icontains=search_query)
        )
    
    paginator = Paginator(all_comments, 4)  # 4 comments per page
    page_number = request.GET.get('page')
    comments = paginator.get_page(page_number)
    comments_count = all_comments.count()

    return render(request, 'tweets/manage_comments.html', {
        'comments': comments,
        'comments_count': comments_count,
        'search_query': search_query
    })


@staff_member_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            # Redirect to manage comments page after updating
            return redirect('tweets:manage_comments')  # must match urls.py name
    else:
        form = CommentForm(instance=comment)

    return render(request, 'tweets/edit_comment.html', {
        'form': form,
        'comment': comment
    })


from django.shortcuts import get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from .models import Comment

@staff_member_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    if request.method == 'POST':
        # Store comment info for success message
        comment_user = comment.user.username
        comment_content = comment.content[:50] + "..." if len(comment.content) > 50 else comment.content
        
        # Delete the comment
        comment.delete()
        
        messages.success(request, f'Comment by {comment_user} ("{comment_content}") has been deleted successfully!')
        return redirect('tweets:manage_comments')
    
    # If GET request, show confirmation page
    return render(request, 'tweets/admin_delete_comment.html', {'comment': comment})




from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.shortcuts import render
from tweets.models import Like   # ✅ import your Like model

@staff_member_required
def manage_likes(request):
    # Get unified search query from URL parameters
    search_query = request.GET.get('search_query', '').strip()
    
    # Base queryset
    likes = Like.objects.select_related('user', 'tweet').all()
    
    # Apply search filter if search query exists
    if search_query:
        # Check if the search query looks like a date (YYYY-MM-DD format)
        import re
        date_pattern = r'^\d{4}-\d{2}-\d{2}$'
        
        if re.match(date_pattern, search_query):
            # Search by date
            likes = likes.filter(created_at__date=search_query)
        else:
            # Search by username
            likes = likes.filter(user__username__icontains=search_query)
    
    # Order by created date (latest first)
    likes = likes.order_by('-created_at')
    
    # Total likes count for badge
    likes_count = likes.count()
    
    # Paginate (4 likes per page)
    paginator = Paginator(likes, 4)
    page_number = request.GET.get('page')
    likes = paginator.get_page(page_number)
    
    return render(request, 'tweets/manage_likes.html', {
        'likes': likes,
        'likes_count': likes_count,
        'search_query': search_query,
    })

from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.shortcuts import render
from tweets.models import Follow
from .forms import FollowForm

@staff_member_required
def manage_follows(request):
    # Get unified search query from URL parameters
    search_query = request.GET.get('search_query', '').strip()
    
    # Base queryset
    follows = Follow.objects.select_related('follower', 'following').all()
    
    # Apply search filter if search query exists
    if search_query:
        # Check if the search query looks like a date (YYYY-MM-DD format)
        import re
        date_pattern = r'^\d{4}-\d{2}-\d{2}$'
        
        if re.match(date_pattern, search_query):
            # Search by date
            follows = follows.filter(created_at__date=search_query)
        else:
            # Search by username (follower or following)
            follows = follows.filter(
                Q(follower__username__icontains=search_query) |
                Q(following__username__icontains=search_query)
            )
    
    # Order by created date (latest first)
    follows = follows.order_by('-created_at')
    
    # Total follows count for badge
    follows_count = follows.count()
    
    # Paginate (4 follows per page)
    paginator = Paginator(follows, 4)
    page_number = request.GET.get('page')
    follows = paginator.get_page(page_number)
    
    return render(request, 'tweets/manage_follows.html', {
        'follows': follows,
        'follows_count': follows_count,
        'search_query': search_query,
    })

@staff_member_required
def edit_follow(request, follow_id):
    follow = get_object_or_404(Follow, id=follow_id)

    if request.method == 'POST':
        form = FollowForm(request.POST, instance=follow)
        if form.is_valid():
            form.save()
            return redirect('tweets:manage_follows')  # redirect after update
    else:
        form = FollowForm(instance=follow)

    return render(request, 'tweets/edit_follow.html', {
        'form': form,
        'follow': follow
    })

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Follow

@staff_member_required
def delete_follow(request, pk):
    follow = get_object_or_404(Follow, pk=pk)
    
    if request.method == 'POST':
        # Store follow info for success message
        follower_username = follow.follower.username
        following_username = follow.following.username
        
        # Delete the follow relationship
        follow.delete()
        
        messages.success(request, f'Follow relationship: {follower_username} → {following_username} has been deleted successfully!')
        return redirect('tweets:manage_follows')
    
    # If GET request, show confirmation page
    return render(request, 'tweets/admin_delete_follow.html', {'follow': follow})



from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.shortcuts import render
from tweets.models import Profile, Tweet, Follow, Like

@staff_member_required
def manage_profiles(request):
    # Get search query from URL parameters
    search_email = request.GET.get('search_email', '').strip()
    
    # Base queryset
    profiles = Profile.objects.select_related('user').all()
    
    # Apply email search filter if search query exists
    if search_email:
        profiles = profiles.filter(user__email__icontains=search_email)
    
    # Order by date joined (newest first)
    profiles = profiles.order_by('-user__date_joined')

    profile_data_list = []
    for profile in profiles:
        user = profile.user
        tweets_count = Tweet.objects.filter(user=user).count()
        followers = Follow.objects.filter(following=user)
        following = Follow.objects.filter(follower=user)

        profile_data_list.append({
            'profile': profile,
            'tweets_count': tweets_count,
            'followers_count': followers.count(),
            'followers_usernames': [f.follower.username for f in followers],
            'following_count': following.count(),
            'following_usernames': [f.following.username for f in following],
            'likes_given': Like.objects.filter(user=user).count(),
            'date_joined': user.date_joined,
        })

    # Paginate (4 profiles per page)
    paginator = Paginator(profile_data_list, 4)
    page_number = request.GET.get('page')
    profile_data = paginator.get_page(page_number)

    return render(request, 'tweets/manage_profiles.html', {
        'profile_data': profile_data,
        'profiles_count': profiles.count(),
        'search_email': search_email,
    })



from django.shortcuts import render, get_object_or_404, redirect
from .models import Profile
from .forms import ProfileForm
from django.contrib import messages

def edit_profile(request, pk):
    profile = get_object_or_404(Profile, pk=pk)
    if request.method == "POST":
        form = AdminProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Check if username is being changed and if it's unique
            new_username = form.cleaned_data['username']
            if new_username != profile.user.username:
                if User.objects.filter(username=new_username).exists():
                    messages.error(request, "Username already exists. Please choose a different username.")
                    return render(request, 'tweets/edit_profile.html', {'form': form})
            
            # Check if email is being changed and if it's unique
            new_email = form.cleaned_data['email']
            if new_email != profile.user.email:
                if User.objects.filter(email=new_email).exists():
                    messages.error(request, "Email already exists. Please choose a different email.")
                    return render(request, 'tweets/edit_profile.html', {'form': form})
            
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('tweets:manage_profiles')
    else:
        form = AdminProfileEditForm(instance=profile)
    return render(request, 'tweets/edit_profile.html', {'form': form})


# views.py
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Profile

@staff_member_required
def delete_profile(request, pk):
    profile = get_object_or_404(Profile, pk=pk)
    
    if request.method == 'POST':
        # Store profile info for success message
        username = profile.user.username
        email = profile.user.email
        
        # Delete the profile (this will also delete the user due to CASCADE)
        profile.delete()
        
        messages.success(request, f'Profile of {username} ({email}) has been deleted successfully!')
        return redirect('tweets:manage_profiles')
    
    # If GET request, show confirmation page
    return render(request, 'tweets/admin_delete_profile.html', {'profile': profile})

    


from django.core.paginator import Paginator

@staff_member_required
def users_table(request):
    # Unified search by username or email
    search_query = request.GET.get('search_query', '').strip()

    users_queryset = User.objects.all()

    if search_query:
        users_queryset = users_queryset.filter(
            Q(username__icontains=search_query) | Q(email__icontains=search_query)
        )

    users_queryset = users_queryset.order_by('-date_joined')

    paginator = Paginator(users_queryset, 4)
    page_number = request.GET.get('page')
    users_page = paginator.get_page(page_number)

    context = {
        'users': users_page,
        'users_count': users_queryset.count(),
        'search_query': search_query,
    }

    return render(request, 'tweets/users_table.html', context)

@staff_member_required
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            # Check if username is being changed and if it already exists
            new_username = form.cleaned_data['username']
            if new_username != user.username:
                if User.objects.filter(username=new_username).exists():
                    messages.error(request, f'Username "{new_username}" already exists. Please choose a different username.')
                    return render(request, 'tweets/edit_user.html', {'form': form, 'user': user})
            
            # Check if email is being changed and if it already exists
            new_email = form.cleaned_data['email']
            if new_email != user.email:
                if User.objects.filter(email=new_email).exists():
                    messages.error(request, f'Email "{new_email}" already exists. Please choose a different email.')
                    return render(request, 'tweets/edit_user.html', {'form': form, 'user': user})
            
            form.save()
            messages.success(request, f'User "{user.username}" has been updated successfully!')
            return redirect('tweets:users_table')
    else:
        form = UserEditForm(instance=user)
    
    return render(request, 'tweets/edit_user.html', {'form': form, 'user': user})

@staff_member_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        # Store user info for success message
        username = user.username
        email = user.email
        
        # Delete the user (this will also delete the profile due to CASCADE)
        user.delete()
        
        messages.success(request, f'User "{username}" ({email}) has been deleted successfully!')
        return redirect('tweets:users_table')
    
    # If GET request, show confirmation page
    return render(request, 'tweets/admin_delete_user.html', {'user': user})

# @user_passes_test(lambda u: u.is_staff)
# def admin_groups(request):
#     groups = Group.objects.all()
#     return render(request, 'tweets/admin_groups.html', {'groups': groups})








# tweets/views.py

# tweets/views.py

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from .models import Follow

def followers_list(request, username):
    user = get_object_or_404(User, username=username)
    # Get all Follow objects where this user is being followed
    followers_qs = Follow.objects.filter(following=user).select_related('follower')
    followers = [f.follower for f in followers_qs]  # Get list of actual User objects
    return render(request, 'tweets/followers_list.html', {
        'profile_user': user,
        'followers': followers
    })


def following_list(request, username):
    user = get_object_or_404(User, username=username)
    # Get all Follow objects where this user is the follower
    following_qs = Follow.objects.filter(follower=user).select_related('following')
    following = [f.following for f in following_qs]  # Get list of actual User objects
    return render(request, 'tweets/following_list.html', {
        'profile_user': user,
        'following': following
    })


from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Tweet

@login_required
def delete_tweet(request, pk):
    tweet = get_object_or_404(Tweet, pk=pk)

    if tweet.user != request.user:
        return redirect('tweets:home')  # or raise PermissionDenied

    tweet.delete()
    return redirect('tweets:home')

@login_required
def edit_tweet(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id, user=request.user)
    if request.method == 'POST':
        form = TweetForm(request.POST, request.FILES, instance=tweet)
        if form.is_valid():
            form.save()
            return redirect('tweets:home')  # Or wherever your tweet list is
    else:
        form = TweetForm(instance=tweet)
    return render(request, 'tweets/edit_tweet.html', {'form': form, 'tweet': tweet})

@staff_member_required
def admin_edit_tweet(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)
    if request.method == 'POST':
        form = AdminTweetEditForm(request.POST, request.FILES, instance=tweet)
        if form.is_valid():
            # Check if username is being changed and if it exists
            new_username = form.cleaned_data['username']
            if new_username != tweet.user.username:
                if not User.objects.filter(username=new_username).exists():
                    messages.error(request, "Username does not exist. Please enter a valid username.")
                    return render(request, 'tweets/admin_edit_tweet.html', {'form': form, 'tweet': tweet})
            
            form.save()
            messages.success(request, "Tweet updated successfully!")
            return redirect('tweets:admin_tweets')
    else:
        form = AdminTweetEditForm(instance=tweet)
    return render(request, 'tweets/admin_edit_tweet.html', {'form': form, 'tweet': tweet})

@staff_member_required
def admin_delete_tweet(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)
    
    if request.method == 'POST':
        # Store tweet info for success message
        tweet_user = tweet.user.username
        tweet_content = tweet.content[:50] + "..." if len(tweet.content) > 50 else tweet.content
        
        # Delete the tweet
        tweet.delete()
        
        messages.success(request, f'Tweet by {tweet_user} ("{tweet_content}") has been deleted successfully!')
        return redirect('tweets:admin_tweets')
    
    # If GET request, show confirmation page
    return render(request, 'tweets/admin_delete_tweet.html', {'tweet': tweet})



def get_trending_topics():
    # Get all tweets from the last 7 days
    recent_tweets = Tweet.objects.all().order_by('-created_at')[:100]

    # Extract words from tweets
    words = []
    for tweet in recent_tweets:
        # Remove special characters and split by spaces
        tweet_words = re.sub(r'[^\w\s]', '', tweet.content.lower()).split()
        # Filter out common words (you can expand this list)
        stop_words = ['the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 'to', 'of', 'in', 'for', 'with', 'on', 'at', 'by', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'my', 'your', 'his', 'her', 'its', 'our', 'their']
        tweet_words = [word for word in tweet_words if word not in stop_words and len(word) > 2]
        words.extend(tweet_words)

    # Count word occurrences
    word_counts = Counter(words)

    # Get the top 5 trending words
    trending = word_counts.most_common(5)

    # Format as list of dictionaries with word and count
    return [{'word': word, 'count': count} for word, count in trending]

def home(request):
    # Show all tweets to everyone
    tweets = Tweet.objects.all()

    # Get user suggestions (users to follow)
    user_suggestions = []
    if request.user.is_authenticated:
        # Get users that the current user already follows
        following_users = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
        # Get users that the current user doesn't follow yet (exclude self and already following)
        user_suggestions = User.objects.exclude(id=request.user.id).exclude(id__in=following_users)[:5]

    # Get trending topics (most used words in recent tweets)
    trending_topics = get_trending_topics()

    form = TweetForm()

    if request.method == 'POST':
        form = TweetForm(request.POST, request.FILES)
        if form.is_valid() and request.user.is_authenticated:
            tweet = form.save(commit=False)
            tweet.user = request.user
            tweet.save()
            messages.success(request, 'Your tweet has been posted!')
            return redirect('tweets:home')

    context = {
        'tweets': tweets,
        'form': form,
        'user_suggestions': user_suggestions,
        'trending_topics': trending_topics,
    }
    return render(request, 'tweets/home.html', context)

def register(request):
    if request.user.is_authenticated:
        return redirect('tweets:home')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('tweets:login')
    else:
        form = UserRegisterForm()

    return render(request, 'tweets/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect('tweets:custom_admin_dashboard')
        return redirect('tweets:home')

    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email')
        password = request.POST.get('password')
        
        # Try to authenticate with username first
        user = authenticate(request, username=username_or_email, password=password)
        
        # If authentication with username fails, try with email
        if user is None:
            # Find user by email safely (avoid MultipleObjectsReturned)
            user_obj = User.objects.filter(email=username_or_email).first()
            if user_obj:
                user = authenticate(request, username=user_obj.username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            if user.is_staff or user.is_superuser:
                return redirect('tweets:custom_admin_dashboard')
            return redirect('tweets:home')
        else:
            messages.error(request, 'Invalid username/email or password.')

    return render(request, 'tweets/login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('tweets:login')

def profile(request, username):
    user = get_object_or_404(User, username=username)

    # If either user has blocked the other, restrict visibility
    is_blocked_by_target = request.user.is_authenticated and Block.objects.filter(blocker=user, blocked=request.user).exists()
    has_blocked_target = request.user.is_authenticated and Block.objects.filter(blocker=request.user, blocked=user).exists()

    if is_blocked_by_target:
        messages.error(request, 'You cannot view this profile.')
        return redirect('tweets:home')

    tweets = Tweet.objects.filter(user=user)
    
    # If user is authenticated, filter out tweets from blocked users
    if request.user.is_authenticated:
        blocked_users = Block.objects.filter(blocker=request.user).values_list('blocked', flat=True)
        blocking_users = Block.objects.filter(blocked=request.user).values_list('blocker', flat=True)
        all_blocked = list(blocked_users) + list(blocking_users)
        tweets = tweets.exclude(user__in=all_blocked)

    # Check if the current user follows this user
    is_following = False
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(follower=request.user, following=user).exists()

    # Get follower and following counts
    followers_count = Follow.objects.filter(following=user).count()
    following_count = Follow.objects.filter(follower=user).count()

    context = {
        'profile_user': user,
        'tweets': tweets,
        'is_following': is_following,
        'followers_count': followers_count,
        'following_count': following_count,
        'has_blocked_target': has_blocked_target,
        'is_blocked_by_target': is_blocked_by_target,
    }

    # If this is the current user's profile, add forms for updating profile
    if request.user.is_authenticated and request.user == user:
        if request.method == 'POST':
            u_form = UserUpdateForm(request.POST, instance=request.user)
            profile_instance, _ = Profile.objects.get_or_create(user=request.user)
            p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile_instance)

            if u_form.is_valid() and p_form.is_valid():
                u_form.save()
                p_form.save()
                messages.success(request, 'Your profile has been updated!')
                return redirect('tweets:profile', username=request.user.username)
        else:
            u_form = UserUpdateForm(instance=request.user)
            profile_instance, _ = Profile.objects.get_or_create(user=request.user)
            p_form = ProfileUpdateForm(instance=profile_instance)

        context.update({
            'u_form': u_form,
            'p_form': p_form,
        })

    return render(request, 'tweets/profile.html', context)

def tweet_detail(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)
    comments = Comment.objects.filter(tweet=tweet)

    # Check if the current user has liked this tweet
    is_liked = False
    if request.user.is_authenticated:
        is_liked = Like.objects.filter(tweet=tweet, user=request.user).exists()

    # Comment form
    if request.method == 'POST' and request.user.is_authenticated:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.tweet = tweet
            comment.user = request.user
            comment.save()
            messages.success(request, 'Your comment has been added!')
            return redirect('tweets:tweet_detail', tweet_id=tweet.id)
    else:
        form = CommentForm()

    context = {
        'tweet': tweet,
        'comments': comments,
        'is_liked': is_liked,
        'form': form,
    }
    return render(request, 'tweets/tweet_detail.html', context)

@login_required
def create_tweet(request):
    if request.method == 'POST':
        form = TweetForm(request.POST, request.FILES)
        if form.is_valid():
            tweet = form.save(commit=False)
            tweet.user = request.user
            tweet.save()
            messages.success(request, 'Your tweet has been posted!')
            return redirect('tweets:home')
    else:
        form = TweetForm()

    return render(request, 'tweets/create_tweet.html', {'form': form})

@login_required
def like_tweet(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)

    # Prevent liking if either user blocked the other
    if Block.objects.filter(blocker=request.user, blocked=tweet.user).exists() or \
       Block.objects.filter(blocker=tweet.user, blocked=request.user).exists():
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'blocked', 'liked': False, 'like_count': tweet.get_like_count()})
        messages.error(request, 'Action not allowed due to blocking.')
        return redirect('tweets:tweet_detail', tweet_id=tweet.id)

    # Check if the user already liked this tweet
    already_liked = Like.objects.filter(tweet=tweet, user=request.user).exists()

    if already_liked:
        # User already liked this tweet, so unlike it
        Like.objects.filter(tweet=tweet, user=request.user).delete()
        liked = False
    else:
        # User hasn't liked this tweet yet, so like it
        Like.objects.create(tweet=tweet, user=request.user)
        liked = True

    # If this is an AJAX request, return JSON response
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': liked,
            'like_count': tweet.get_like_count(),
        })

    # Get the referring page
    referer = request.META.get('HTTP_REFERER')

    # If coming from tweet detail page, redirect back there
    if referer and f'/tweet/{tweet_id}/' in referer:
        return redirect('tweets:tweet_detail', tweet_id=tweet.id)

    # Otherwise, redirect to home
    return redirect('tweets:home')

@login_required
def add_comment(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)

    # Prevent commenting if either user blocked the other
    if Block.objects.filter(blocker=request.user, blocked=tweet.user).exists() or \
       Block.objects.filter(blocker=tweet.user, blocked=request.user).exists():
        messages.error(request, 'Action not allowed due to blocking.')
        return redirect('tweets:tweet_detail', tweet_id=tweet.id)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.tweet = tweet
            comment.user = request.user
            comment.save()
            messages.success(request, 'Your comment has been added!')

    return redirect('tweets:tweet_detail', tweet_id=tweet.id)

@login_required
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)

    # Don't allow users to follow themselves
    if request.user == user_to_follow:
        messages.error(request, 'You cannot follow yourself.')
        return redirect('tweets:profile', username=username)

    # Prevent following if either has blocked the other
    if Block.objects.filter(blocker=request.user, blocked=user_to_follow).exists() or \
       Block.objects.filter(blocker=user_to_follow, blocked=request.user).exists():
        messages.error(request, 'Action not allowed due to blocking.')
        return redirect('tweets:profile', username=username)

    # Create the follow relationship if it doesn't exist
    follow, created = Follow.objects.get_or_create(follower=request.user, following=user_to_follow)

    if created:
        messages.success(request, f'You are now following {username}!')
    else:
        messages.info(request, f'You are already following {username}.')

    return redirect('tweets:profile', username=username)

@login_required
def unfollow_user(request, username):
    user_to_unfollow = get_object_or_404(User, username=username)

    # Try to find the follow relationship
    try:
        follow = Follow.objects.get(follower=request.user, following=user_to_unfollow)
        follow.delete()
        messages.success(request, f'You have unfollowed {username}.')
    except Follow.DoesNotExist:
        messages.info(request, f'You are not following {username}.')

    return redirect('tweets:profile', username=username)

@login_required
def block_user(request, username):
    target = get_object_or_404(User, username=username)
    if target == request.user:
        messages.error(request, 'You cannot block yourself.')
        return redirect('tweets:profile', username=username)
    Block.objects.get_or_create(blocker=request.user, blocked=target)
    # Remove follow relationships in both directions
    Follow.objects.filter(follower=request.user, following=target).delete()
    Follow.objects.filter(follower=target, following=request.user).delete()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'blocked'})
    messages.success(request, f'You have blocked {username}.')
    return redirect('tweets:profile', username=username)

@login_required
def unblock_user(request, username):
    target = get_object_or_404(User, username=username)
    Block.objects.filter(blocker=request.user, blocked=target).delete()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'unblocked'})
    messages.success(request, f'You have unblocked {username}.')
    return redirect('tweets:profile', username=username)

def search(request):
    query = request.GET.get('q', '')
    users = []
    tweets = []

    if query:
        # Search for users by username or email
        users = User.objects.filter(Q(username__icontains=query) | Q(email__icontains=query))

        # Search for tweets by content
        tweets = Tweet.objects.filter(content__icontains=query)

    context = {
        'query': query,
        'users': users,
        'tweets': tweets,
    }

    return render(request, 'tweets/search_results.html', context)

def simple_password_reset(request):
    """Simple password reset using username or email"""
    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Try to find user by username first
        try:
            user = User.objects.get(username=username_or_email)
        except User.DoesNotExist:
            # If not found by username, try to find by email
            try:
                user = User.objects.get(email=username_or_email)
            except User.DoesNotExist:
                messages.error(request, 'Username or email not found. Please check your input.')
                return render(request, 'tweets/simple_password_reset.html')

        # Check if passwords match
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match. Please try again.')
            return render(request, 'tweets/simple_password_reset.html')

        # Check password length
        if len(new_password) < 6:
            messages.error(request, 'Password must be at least 6 characters long.')
            return render(request, 'tweets/simple_password_reset.html')

        # Update password
        user.set_password(new_password)
        user.save()

        # Send email notification
        try:
            # Prepare email context
            context = {
                'user': user,
                'reset_date': timezone.now().strftime('%B %d, %Y at %I:%M %p UTC'),
            }
            
            # Render email templates
            html_content = render_to_string('tweets/emails/password_reset_notification.html', context)
            text_content = render_to_string('tweets/emails/password_reset_notification.txt', context)
            
            # Create email
            subject = 'Your Password Has Been Changed'
            from_email = 'Twitter Clone <noreply@twitterclone.com>'
            to_email = [user.email]
            
            # Create multi-part email (HTML and text)
            email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
            email.attach_alternative(html_content, "text/html")
            
            # Send email
            email.send()
            
            messages.success(request, f'Password successfully changed for {user.username}! A confirmation email has been sent to {user.email}.')
            
        except Exception as e:
            # If email sending fails, still show success message but log the error
            messages.success(request, f'Password successfully changed for {user.username}! You can now login with your new password.')
            messages.warning(request, 'Note: We were unable to send a confirmation email. Please contact support if needed.')
            print(f"Email sending failed: {e}")  # Log error for debugging

        return redirect('tweets:login')

    return render(request, 'tweets/simple_password_reset.html')


def edit_tweet(request, tweet_id):

    tweet = get_object_or_404(Tweet, id=tweet_id, user=request.user)

    if request.method == 'POST':

        form = TweetForm(request.POST, request.FILES, instance=tweet)

        if form.is_valid():

            form.save()

            return redirect('tweets:home')  # Or wherever your tweet list is

    else:

        form = TweetForm(instance=tweet)

    return render(request, 'tweets/edit_tweet.html', {'form': form, 'tweet': tweet})



@staff_member_required

def admin_edit_tweet(request, tweet_id):

    tweet = get_object_or_404(Tweet, id=tweet_id)

    if request.method == 'POST':

        form = AdminTweetEditForm(request.POST, request.FILES, instance=tweet)

        if form.is_valid():

            # Check if username is being changed and if it exists

            new_username = form.cleaned_data['username']

            if new_username != tweet.user.username:

                if not User.objects.filter(username=new_username).exists():

                    messages.error(request, "Username does not exist. Please enter a valid username.")

                    return render(request, 'tweets/admin_edit_tweet.html', {'form': form, 'tweet': tweet})

            

            form.save()

            messages.success(request, "Tweet updated successfully!")

            return redirect('tweets:admin_tweets')

    else:

        form = AdminTweetEditForm(instance=tweet)

    return render(request, 'tweets/admin_edit_tweet.html', {'form': form, 'tweet': tweet})



@staff_member_required

def admin_delete_tweet(request, tweet_id):

    tweet = get_object_or_404(Tweet, id=tweet_id)

    

    if request.method == 'POST':

        # Store tweet info for success message

        tweet_user = tweet.user.username

        tweet_content = tweet.content[:50] + "..." if len(tweet.content) > 50 else tweet.content

        

        # Delete the tweet

        tweet.delete()

        

        messages.success(request, f'Tweet by {tweet_user} ("{tweet_content}") has been deleted successfully!')

        return redirect('tweets:admin_tweets')

    

    # If GET request, show confirmation page

    return render(request, 'tweets/admin_delete_tweet.html', {'tweet': tweet})







def get_trending_topics():

    # Get all tweets from the last 7 days

    recent_tweets = Tweet.objects.all().order_by('-created_at')[:100]



    # Extract words from tweets

    words = []

    for tweet in recent_tweets:

        # Remove special characters and split by spaces

        tweet_words = re.sub(r'[^\w\s]', '', tweet.content.lower()).split()

        # Filter out common words (you can expand this list)

        stop_words = ['the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 'to', 'of', 'in', 'for', 'with', 'on', 'at', 'by', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'my', 'your', 'his', 'her', 'its', 'our', 'their']

        tweet_words = [word for word in tweet_words if word not in stop_words and len(word) > 2]

        words.extend(tweet_words)



    # Count word occurrences

    word_counts = Counter(words)



    # Get the top 5 trending words

    trending = word_counts.most_common(5)



    # Format as list of dictionaries with word and count

    return [{'word': word, 'count': count} for word, count in trending]



def home(request):

    # Show all tweets to everyone, but exclude tweets from blocked users
    tweets = Tweet.objects.all()
    
    # If user is authenticated, filter out tweets from users they've blocked or who have blocked them
    if request.user.is_authenticated:
        blocked_users = Block.objects.filter(blocker=request.user).values_list('blocked', flat=True)
        blocking_users = Block.objects.filter(blocked=request.user).values_list('blocker', flat=True)
        all_blocked = list(blocked_users) + list(blocking_users)
        tweets = tweets.exclude(user__in=all_blocked)



    # Get user suggestions (users to follow)

    user_suggestions = []

    if request.user.is_authenticated:

        # Get users that the current user already follows
        following_users = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
        
        # Get blocked users (both directions)
        blocked_users = Block.objects.filter(blocker=request.user).values_list('blocked', flat=True)
        blocking_users = Block.objects.filter(blocked=request.user).values_list('blocker', flat=True)
        all_blocked = list(blocked_users) + list(blocking_users)

        # Get users that the current user doesn't follow yet (exclude self, already following, and blocked users)
        user_suggestions = User.objects.exclude(id=request.user.id).exclude(id__in=following_users).exclude(id__in=all_blocked)[:5]



    # Get trending topics (most used words in recent tweets)

    trending_topics = get_trending_topics()



    form = TweetForm()



    if request.method == 'POST':

        form = TweetForm(request.POST, request.FILES)

        if form.is_valid() and request.user.is_authenticated:

            tweet = form.save(commit=False)

            tweet.user = request.user

            tweet.save()

            messages.success(request, 'Your tweet has been posted!')

            return redirect('tweets:home')



    context = {

        'tweets': tweets,

        'form': form,

        'user_suggestions': user_suggestions,

        'trending_topics': trending_topics,

    }

    return render(request, 'tweets/home.html', context)



def register(request):

    if request.user.is_authenticated:

        return redirect('tweets:home')



    if request.method == 'POST':

        form = UserRegisterForm(request.POST)

        if form.is_valid():

            user = form.save()

            username = form.cleaned_data.get('username')

            messages.success(request, f'Account created for {username}! You can now log in.')

            return redirect('tweets:login')

    else:

        form = UserRegisterForm()



    return render(request, 'tweets/register.html', {'form': form})



def login_view(request):

    if request.user.is_authenticated:

        if request.user.is_staff or request.user.is_superuser:

            return redirect('tweets:custom_admin_dashboard')

        return redirect('tweets:home')



    if request.method == 'POST':

        username_or_email = request.POST.get('username_or_email')

        password = request.POST.get('password')

        

        # Try to authenticate with username first

        user = authenticate(request, username=username_or_email, password=password)

        

        # If authentication with username fails, try with email

        if user is None:

            try:

                # Find user by email

                user_obj = User.objects.get(email=username_or_email)

                user = authenticate(request, username=user_obj.username, password=password)

            except User.DoesNotExist:

                user = None



        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            if user.is_staff or user.is_superuser:
                return redirect('tweets:custom_admin_dashboard')
            return redirect('tweets:home')

        else:

            messages.error(request, 'Invalid username/email or password.')



    return render(request, 'tweets/login.html')



@login_required

def logout_view(request):

    logout(request)

    messages.success(request, 'You have been logged out.')

    return redirect('tweets:login')



def profile(request, username):

    user = get_object_or_404(User, username=username)

    # If either user has blocked the other, restrict visibility
    is_blocked_by_target = request.user.is_authenticated and Block.objects.filter(blocker=user, blocked=request.user).exists()
    has_blocked_target = request.user.is_authenticated and Block.objects.filter(blocker=request.user, blocked=user).exists()

    if is_blocked_by_target:
        messages.error(request, 'You cannot view this profile.')
        return redirect('tweets:home')

    tweets = Tweet.objects.filter(user=user)
    
    # If user is authenticated, filter out tweets from blocked users
    if request.user.is_authenticated:
        blocked_users = Block.objects.filter(blocker=request.user).values_list('blocked', flat=True)
        blocking_users = Block.objects.filter(blocked=request.user).values_list('blocker', flat=True)
        all_blocked = list(blocked_users) + list(blocking_users)
        tweets = tweets.exclude(user__in=all_blocked)



    # Check if the current user follows this user

    is_following = False

    if request.user.is_authenticated:

        is_following = Follow.objects.filter(follower=request.user, following=user).exists()



    # Get follower and following counts

    followers_count = Follow.objects.filter(following=user).count()

    following_count = Follow.objects.filter(follower=user).count()



    context = {

        'profile_user': user,

        'tweets': tweets,

        'is_following': is_following,

        'followers_count': followers_count,

        'following_count': following_count,
        'has_blocked_target': has_blocked_target,
        'is_blocked_by_target': is_blocked_by_target,

    }



    # If this is the current user's profile, add forms for updating profile

    if request.user.is_authenticated and request.user == user:

        if request.method == 'POST':

            u_form = UserUpdateForm(request.POST, instance=request.user)

            p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)



            if u_form.is_valid() and p_form.is_valid():

                u_form.save()

                p_form.save()

                messages.success(request, 'Your profile has been updated!')

                return redirect('tweets:profile', username=request.user.username)

        else:

            u_form = UserUpdateForm(instance=request.user)

            p_form = ProfileUpdateForm(instance=request.user.profile)



        context.update({

            'u_form': u_form,

            'p_form': p_form,

        })



    return render(request, 'tweets/profile.html', context)



def tweet_detail(request, tweet_id):

    tweet = get_object_or_404(Tweet, id=tweet_id)

    comments = Comment.objects.filter(tweet=tweet)



    # Check if the current user has liked this tweet

    is_liked = False

    if request.user.is_authenticated:

        is_liked = Like.objects.filter(tweet=tweet, user=request.user).exists()



    # Comment form

    if request.method == 'POST' and request.user.is_authenticated:

        form = CommentForm(request.POST)

        if form.is_valid():

            comment = form.save(commit=False)

            comment.tweet = tweet

            comment.user = request.user

            comment.save()

            messages.success(request, 'Your comment has been added!')

            return redirect('tweets:tweet_detail', tweet_id=tweet.id)

    else:

        form = CommentForm()



    context = {

        'tweet': tweet,

        'comments': comments,

        'is_liked': is_liked,

        'form': form,

    }

    return render(request, 'tweets/tweet_detail.html', context)



@login_required

def create_tweet(request):

    if request.method == 'POST':

        form = TweetForm(request.POST, request.FILES)

        if form.is_valid():

            tweet = form.save(commit=False)

            tweet.user = request.user

            tweet.save()

            messages.success(request, 'Your tweet has been posted!')

            return redirect('tweets:home')

    else:

        form = TweetForm()



    return render(request, 'tweets/create_tweet.html', {'form': form})



@login_required

def like_tweet(request, tweet_id):

    tweet = get_object_or_404(Tweet, id=tweet_id)



    # Check if the user already liked this tweet

    already_liked = Like.objects.filter(tweet=tweet, user=request.user).exists()



    if already_liked:

        # User already liked this tweet, so unlike it

        Like.objects.filter(tweet=tweet, user=request.user).delete()

        liked = False

    else:

        # User hasn't liked this tweet yet, so like it

        Like.objects.create(tweet=tweet, user=request.user)

        liked = True



    # If this is an AJAX request, return JSON response

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':

        return JsonResponse({

            'liked': liked,

            'like_count': tweet.get_like_count(),

        })



    # Get the referring page

    referer = request.META.get('HTTP_REFERER')



    # If coming from tweet detail page, redirect back there

    if referer and f'/tweet/{tweet_id}/' in referer:

        return redirect('tweets:tweet_detail', tweet_id=tweet.id)



    # Otherwise, redirect to home

    return redirect('tweets:home')



@login_required

def add_comment(request, tweet_id):

    tweet = get_object_or_404(Tweet, id=tweet_id)



    if request.method == 'POST':

        form = CommentForm(request.POST)

        if form.is_valid():

            comment = form.save(commit=False)

            comment.tweet = tweet

            comment.user = request.user

            comment.save()

            messages.success(request, 'Your comment has been added!')



    return redirect('tweets:tweet_detail', tweet_id=tweet.id)



@login_required

def follow_user(request, username):

    user_to_follow = get_object_or_404(User, username=username)



    # Don't allow users to follow themselves

    if request.user == user_to_follow:

        messages.error(request, 'You cannot follow yourself.')

        return redirect('tweets:profile', username=username)



    # Create the follow relationship if it doesn't exist

    follow, created = Follow.objects.get_or_create(follower=request.user, following=user_to_follow)



    if created:

        messages.success(request, f'You are now following {username}!')

    else:

        messages.info(request, f'You are already following {username}.')



    return redirect('tweets:profile', username=username)



@login_required

def unfollow_user(request, username):

    user_to_unfollow = get_object_or_404(User, username=username)



    # Try to find the follow relationship

    try:

        follow = Follow.objects.get(follower=request.user, following=user_to_unfollow)

        follow.delete()

        messages.success(request, f'You have unfollowed {username}.')

    except Follow.DoesNotExist:

        messages.info(request, f'You are not following {username}.')



    return redirect('tweets:profile', username=username)



def search(request):

    query = request.GET.get('q', '')

    users = []

    tweets = []



    if query:

        # Search for users by username or email

        users = User.objects.filter(Q(username__icontains=query) | Q(email__icontains=query))



        # Search for tweets by content

        tweets = Tweet.objects.filter(content__icontains=query)



    context = {

        'query': query,

        'users': users,

        'tweets': tweets,

    }



    return render(request, 'tweets/search_results.html', context)



def simple_password_reset(request):

    """Simple password reset using username or email"""

    if request.method == 'POST':

        username_or_email = request.POST.get('username_or_email')

        new_password = request.POST.get('new_password')

        confirm_password = request.POST.get('confirm_password')



        # Try to find user by username first

        try:

            user = User.objects.get(username=username_or_email)

        except User.DoesNotExist:

            # If not found by username, try to find by email

            try:

                user = User.objects.get(email=username_or_email)

            except User.DoesNotExist:

                messages.error(request, 'Username or email not found. Please check your input.')

                return render(request, 'tweets/simple_password_reset.html')



        # Check if passwords match

        if new_password != confirm_password:

            messages.error(request, 'Passwords do not match. Please try again.')

            return render(request, 'tweets/simple_password_reset.html')



        # Check password length

        if len(new_password) < 6:

            messages.error(request, 'Password must be at least 6 characters long.')

            return render(request, 'tweets/simple_password_reset.html')



        # Update password

        user.set_password(new_password)

        user.save()



        # Send email notification

        try:

            # Prepare email context

            context = {

                'user': user,

                'reset_date': timezone.now().strftime('%B %d, %Y at %I:%M %p UTC'),

            }

            

            # Render email templates

            html_content = render_to_string('tweets/emails/password_reset_notification.html', context)

            text_content = render_to_string('tweets/emails/password_reset_notification.txt', context)

            

            # Create email

            subject = 'Your Password Has Been Changed'

            from_email = 'Twitter Clone <noreply@twitterclone.com>'

            to_email = [user.email]

            

            # Create multi-part email (HTML and text)

            email = EmailMultiAlternatives(subject, text_content, from_email, to_email)

            email.attach_alternative(html_content, "text/html")

            

            # Send email

            email.send()

            

            messages.success(request, f'Password successfully changed for {user.username}! A confirmation email has been sent to {user.email}.')

            

        except Exception as e:

            # If email sending fails, still show success message but log the error

            messages.success(request, f'Password successfully changed for {user.username}! You can now login with your new password.')

            messages.warning(request, 'Note: We were unable to send a confirmation email. Please contact support if needed.')

            print(f"Email sending failed: {e}")  # Log error for debugging



        return redirect('tweets:login')



    return render(request, 'tweets/simple_password_reset.html')


