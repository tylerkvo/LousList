from django.contrib import admin
from .models import Department, SocialUser, ClassObj, ScheduleComment, Schedule

admin.site.register(Department)
admin.site.register(SocialUser)
admin.site.register(ClassObj)
admin.site.register(ScheduleComment)
admin.site.register(Schedule)