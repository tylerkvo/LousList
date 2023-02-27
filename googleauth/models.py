from django.db import models
from django.contrib.auth.models import User
import datetime

# Create your models here.
class Department(models.Model):
    dept = models.CharField(max_length=10)
    instructor = models.CharField(max_length = 20, default="", blank=True)
    course_num =  models.CharField(max_length=5, default="", blank=True)
    open_seats = models.BooleanField(blank=True, default=False)
    
class SocialUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(default="")
    friends = models.ManyToManyField(User,related_name='friended_by')

    def __str__(self):
        return self.user.username
    
class ClassObj(models.Model):
    subject = models.TextField(default="")
    catalog_number = models.TextField(default="")
    course_number = models.TextField(default="")
    name = models.TextField(default="")
    email = models.TextField(default="")
    semester_code = models.TextField(default="")
    course_section = models.TextField(default="")
    description = models.TextField(default="")
    units = models.TextField(default="")
    component = models.TextField(default="")
    class_capacity = models.TextField(default="")
    wait_list = models.TextField(default="")
    wait_cap = models.TextField(default="")
    enrollment_total = models.TextField(default="")
    enrollment_available = models.TextField(default="")
    days = models.TextField(default="")
    start_time = models.TextField(default="")
    end_time = models.TextField(default="")
    facility_description = models.TextField(default="")
    topic = models.TextField(default="")
    
    susers = models.ManyToManyField(SocialUser)
    
    def __str__(self):
        return self.subject + self.catalog_number

class Schedule(models.Model):
    name = models.TextField(default="")
    classes = models.ManyToManyField(ClassObj, blank=True)
    user = models.ForeignKey(SocialUser, on_delete=models.CASCADE, blank=True)

    def __str__(self):
        return self.name

class ScheduleComment(models.Model):
    schedule_owner = models.ForeignKey(SocialUser, on_delete=models.CASCADE,related_name="schedule_comments")
    comment_poster = models.ForeignKey(SocialUser, on_delete=models.SET_NULL,null=True)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE,blank=True,default=None)
    # This is for the purpose if a user gets deleted but their name should remain without a user reference
    commentor_name = models.CharField(default="",max_length=50)
    
    comment = models.TextField(default="")
    pub_date = models.DateTimeField('date published',default=datetime.datetime(2022,11,9))
    
    def __str__(self):
        return self.comment_poster.user.username + " to " + self.schedule_owner.user.username + " " + str(self.pk)


    