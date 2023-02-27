from django import forms
from .models import Department, SocialUser, Schedule

from django.contrib.auth.models import User

class UpdateUserForm(forms.ModelForm):
    username = forms.CharField(max_length=100,required=True,widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ['username']
        
class UpdateSocialUserForm(forms.ModelForm):
    bio = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}))
    
    class Meta:
        model = SocialUser
        fields = ['bio']

class ScheduleForm(forms.ModelForm):
    name = forms.CharField(max_length=100,required=True,widget=forms.TextInput(attrs={'class': 'form-control'}))
    class Meta:
        model = Schedule
        fields = ['name']

# Django - Update User Profile
# https://dev.to/earthcomfy/django-update-user-profile-33ho 

class DeptForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = '__all__'
   
        """
class ClassObjForm(forms.ModelForm):
    subject = forms.TextField(default="")
    catalog_number = forms.TextField(default="")
    course_number = forms.TextField(default="")
    name = forms.TextField(default="")
    email = forms.TextField(default="")
    semester_code = forms.TextField(default="")
    course_section = forms.TextField(default="")
    description = forms.TextField(default="")
    units = forms.TextField(default="")
    component = forms.TextField(default="")
    class_capacity = forms.TextField(default="")
    wait_list = forms.TextField(default="")
    wait_cap = forms.TextField(default="")
    enrollment_total = forms.TextField(default="")
    enrollment_available = forms.TextField(default="")
    topic = forms.TextField(default="")
    days = forms.TextField(default="")
    start_time = forms.TextField(default="")
    end_time = forms.TextField(default="")
    facility_description = forms.TextField(default="")
    """