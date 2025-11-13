from django.urls import path
from . import views

app_name = 'tweets'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('tweet/<int:tweet_id>/', views.tweet_detail, name='tweet_detail'),
    path('tweet/create/', views.create_tweet, name='create_tweet'),
    path('tweet/<int:tweet_id>/like/', views.like_tweet, name='like_tweet'),
    path('tweet/<int:tweet_id>/comment/', views.add_comment, name='add_comment'),
    path('follow/<str:username>/', views.follow_user, name='follow_user'),
    path('unfollow/<str:username>/', views.unfollow_user, name='unfollow_user'),
    path('block/<str:username>/', views.block_user, name='block_user'),
    path('unblock/<str:username>/', views.unblock_user, name='unblock_user'),
    path('search/', views.search, name='search'),

    # Simple password reset (username + new password only)
    path('password-reset/', views.simple_password_reset, name='password_reset'),

    path('<str:username>/followers/', views.followers_list, name='followers_list'),
    path('<str:username>/following/', views.following_list, name='following_list'),
    path('tweet/<int:pk>/delete/', views.delete_tweet, name='delete_tweet'),
    path('edit/<int:tweet_id>/', views.edit_tweet, name='edit_tweet'),

    path('admin_login/', views.admin1, name='admin_login'),
    path('custom_admin/', views.custom_admin_dashboard, name='custom_admin_dashboard'),
    # # Data pages
    path('custom_admin/admin_tweets/', views.admin_tweets, name='admin_tweets'),
    path('custom_admin/admin_tweets/edit/<int:tweet_id>/', views.admin_edit_tweet, name='admin_edit_tweet'),
    path('custom_admin/admin_tweets/delete/<int:tweet_id>/', views.admin_delete_tweet, name='admin_delete_tweet'),  


    path('custom_admin/manage_comments/', views.manage_comments, name='manage_comments'),
    path('comments/edit/<int:comment_id>/', views.edit_comment, name='edit_comment'),
    path('comments/delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),


    path('custom_admin/manage_likes/', views.manage_likes, name='manage_likes'),
    
    path('custom_admin/manage_follows/', views.manage_follows, name='manage_follows'),
    path('follows/edit/<int:follow_id>/', views.edit_follow, name='edit_follow'),
    path('follow/<int:pk>/delete/', views.delete_follow, name='delete_follow'),
    path('follow/', views.followers_list, name='followers_list'), 

    path('custom_admin/manage_profiles/', views.manage_profiles, name='manage_profiles'),
    path('profiles/edit/<int:pk>/', views.edit_profile, name='edit_profile'),
     path('custom_admin/profile/<int:pk>/delete/', views.delete_profile, name='delete_profile'),

     
    path('custom_admin/users_table/', views.users_table, name='users_table'),
    path('custom_admin/users_table/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('custom_admin/users_table/delete/<int:user_id>/', views.delete_user, name='delete_user'),



    # path('admin-dashboard/groups/', views.admin_groups, name='admin_groups'),


     path('tweet/<int:tweet_id>/edit/', views.edit_tweet, name='edit_tweet'),

     

]
