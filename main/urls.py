from django.urls import path
from .import  views
from django.urls import path,re_path
app_name = 'main'
urlpatterns = [
    path('',views.homePage, name='homepage'),
    path('login/',views.loginUser, name='login'),
    path('currentUserConnectUserList/',views.currentUserConnectUserList, name='currentUserConnectUserList'),
    path('home/',views.logged_user, name='home'),
    # path('messages/<str:user>/',views.messagesu, name='messagesu'),
    path('message_detail/<int:messageId>/',views.message_detail, name='message_detail'),
    path('logout/',views.logout_view, name='logout'),
    path('explore/',views.explore, name='explore'),
    path('profile/<int:pk>',views.profile, name='profile'),
    path('register/',views.register, name='register'),
    path('networks/<str:typeOf>',views.networks, name='networks'),
    path('connect/',views.connect, name='connect'),
    path('connect-list/',views.connect_list, name='connect_list'),
    path('users/<int:pk>/', views.connect_list_view, name='connect_list_view'),
    path('connect/cancel/<int:pk>/', views.cancel, name='cancel'),
    path('connect/cancel_admin/<int:pk>/', views.cancel_admin, name='cancel_admin'),
    path('connect/active_admin/<int:pk>/', views.active_admin, name='active_admin'),

    path('connect/accept/<int:pk>/', views.accept, name='accept'),
    path('users/', views.users_list, name='users_list'),
    path('filter/<str:typeOf>', views.filter, name='filter'),
    path('get-content/<str:typeOf>', views.getContent, name='get_content'),
    re_path(r'^users/cancel/(?P<id>[\w-]+)/$', views.cancel_friend_request),
    re_path(r'^users/accept/(?P<id>[\w-]+)/$', views.accept_friend_request),
    re_path(r'^users/delete/(?P<id>[\w-]+)/$', views.delete_friend_request),
    # path('compose/', views.ComposeMessageView.as_view(), name='m_compose'),
    path('message/compose', views.m_compose, name='m_compose'),
    path('message/inbox', views.m_inbox, name='m_inbox'),
    path('message/outbox', views.m_outbox, name='m_outbox'),
    
    path('send/', views.sentMessage, name='sentMessage'),
    path('sentMessagefromDetail/', views.sentMessagefromDetail, name='sentMessagefromDetail'),

    
    path('connection/connected', views.c_connected, name='c_connected'),
    path('connection/sent', views.c_sent, name='c_sent'),
    path('connection/recieved', views.c_recived, name='c_recived'),
    path('profile/list', views.profile_list, name='profile_list'),
    path('contacted_list/',views.contacted_list, name='contacted_list'),

    path('saveContact/',views.saveContact, name='saveContact'),
    path('admin/',views.admin, name='admin'),
    path('connection_list/',views.connection_list, name='connection_list'),
    path('message_list/',views.message_list, name='message_list'),
    path('adminLogin/',views.adminLogin, name='adminLogin'),

    path('activate_profile/<int:id>/', views.activate_profile, name='activate_profile'),
    path('decativate_profile/<int:id>/', views.decativate_profile, name='decativate_profile'),

]

