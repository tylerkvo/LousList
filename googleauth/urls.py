from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('about', views.about, name='about'),
    path('search', views.search, name='search'),
    path('searchresults', views.searchresults, name='searchresults'),
    path('schedule', views.schedule_list, name='schedulelist'),
    path('addschedule', views.add_schedule, name='addschedule'),
    path('deleteschedule/<int:sched_id>', views.delete_schedule, name='deleteschedule'),
    path('schedule/<int:sched_id>', views.schedule, name='schedule'),
    path('addclass/<int:sched_id>/<int:class_id>', views.add_class_to_schedule, name='addclass'),
    path('removeclass/<int:sched_id>/<int:class_id>', views.remove_class_from_schedule, name='removeclass'),
    path('deleteclass/<int:class_id>', views.delete_class, name='deleteclass'),
    path('profile', views.profile, name='profile'),
    path('profile/<int:socialuser_id>', views.profile_specific, name='profile_specific'),
    path('interested/<str:course_name>', views.interested, name='interested'),
    path('add_friend/<int:socialuser_id>', views.add_friend, name='add_friend'),
    path('remove_friend/<int:socialuser_id>', views.remove_friend, name='remove_friend'),
    path('searchpeople', views.search_people, name='searchpeople'),
    path('add_comment/', views.add_comment, name='add_comment'),
    path('delete_comment/', views.delete_comment, name='delete_comment')
]
