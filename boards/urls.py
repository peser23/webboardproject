from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('boards/<int:pk>/', views.BoardTopicsListView.as_view(), name='board_topics'),
    path('boards/<int:pk>/new_topic', views.new_topic, name='new_topic'),
    path('boards/<int:pk>/topics/<int:topic_pk>/', views.TopicPostsListView.as_view(), name='topic_posts'),
    path('boards/<int:pk>/topics/<int:topic_pk>/reply', views.reply_topic, name='reply_topic'),
    path('boards/<int:pk>/topics/<int:topic_pk>/posts/<int:post_pk>/edit',
         views.PostUpdateView.as_view(), name='edit_post'),
    path('settings/account/', views.UserUpdateView.as_view(), name='my_account')
]