from django.shortcuts import render, get_object_or_404
import requests
from django.template.defaulttags import register
from .forms import DeptForm, UpdateUserForm, UpdateSocialUserForm, ScheduleForm
from django.http import HttpResponseRedirect,HttpResponseNotFound
from django.shortcuts import redirect

from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.contrib.auth.models import User

from datetime import datetime

from django.urls import reverse
from .models import Department, ClassObj, SocialUser, Schedule, ScheduleComment


def login(request):
    if not request.user.is_authenticated:
        return render(request, 'googleauth/index.html')
    else:
        return render(request, 'googleauth/index.html', {'id':request.user.socialuser.id})

@login_required
def about(request):
    return render(request, 'googleauth/about.html', {'id':request.user.socialuser.id})

@login_required
def search(request):
    deptsGet = requests.get('http://luthers-list.herokuapp.com/api/deptlist/?format=json')
    deptsJson = deptsGet.json()
    deptsList = [dept['subject'] for dept in deptsJson] #list of all of the department mnemonics

    if request.method == 'POST':
        form = DeptForm(request.POST)
        #check input - if dept not valid then throw message
        #completed using https://docs.djangoproject.com/en/4.1/ref/contrib/messages/
        if form.data['dept'] not in deptsList:
            messages.error(request, 'Enter a valid department')
            return render(request, 'googleauth/search.html', {'deptsList':deptsList, 'form':form, 'messages': messages.get_messages(request)})

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('searchresults'))
    else:
        form = DeptForm()

    return render(request, 'googleauth/search.html', {'deptsList':deptsList, 'form':form, 'id':request.user.socialuser.id})

@login_required
def searchresults(request):
    #get last submission to form, along with all individual attributes
    latest_dept = Department.objects.last()
    dept_attr = getattr(latest_dept, 'dept')
    instr_attr = getattr(latest_dept, 'instructor')
    instr_attr = instr_attr.casefold() #case insensitive matching
    course_num_attr = getattr(latest_dept, 'course_num')
    open_seats_attr = getattr(latest_dept, 'open_seats')
    
    #get data from api and put in list format for given dept
    data = requests.get('http://luthers-list.herokuapp.com/api/dept/%s/?format=json' % (dept_attr))
    classList = data.json()
    #create lists to store instructor, course_num and open_seats matching elements in classList
    #filter by instructor
    instr_list = [i for i in classList if instr_attr in i['instructor']['name'].casefold() or instr_attr == i['instructor']['name'].casefold()] #ensure case insensitive search]

    #filter by course_number
    num_list = [i for i in classList if course_num_attr in i['catalog_number'] or course_num_attr == i['catalog_number']]

    #filter by open seats
    if open_seats_attr:
        open_list = [i for i in classList if i['enrollment_available'] > 0]
    else:
        open_list = [] 

    #utilize sets to find common elements between the lists (& is the intersection operator)
    if open_list and num_list and instr_list:
        filteredList = [x for x in open_list if x in num_list and x in instr_list]
    elif open_list and num_list:
        filteredList = [x for x in open_list if x in num_list]
    elif open_list and instr_list:
        filteredList = [x for x in open_list if x in instr_list]
    elif num_list and instr_list:
        filteredList = [x for x in instr_list if x in num_list]
    else: #if its just one of them, add them all together, since only one will have elements
        filteredList = num_list + open_list + instr_list

    #look through classList to find classes with multiple sections of the same catalog_number (like 1010 in CS 1010)
    mapping = {} #dict to hold the mapping from catalog_number to information in that listing
    for c in filteredList:
        course = c['catalog_number']
        if course not in mapping:
            mapping[course] = [c]
        else:
            mapping[course].append(c)
 
    return render(request,  'googleauth/searchresults.html', {'latest_dept': dept_attr, 'classList': mapping, 'id':request.user.socialuser.id})

def convert_time(time): #method to convert luther's list time format to traditional hh:mm format
    x = time.split('.')
    ampm = "am"
    if x[0] != "":
        if int(x[0]) > 12: #if past 12 then we need to modulus by 12 to get pm time
            x[0] = int(x[0]) % 12
            ampm = "pm"
        elif int(x[0]) == 12: #handle case of noon (pm but no modulus)
            ampm = "pm"
        return str(x[0]) + ":" + str(x[1]) + ampm
    return time

def find_conflicts(classes): #method to determine conflicting classes in a given day's class dict
    l = list(classes.items()) 
    conflicts = set()
    for i, j in enumerate(l):
        if i > 0:
            #get the prev end time hour and current start time hour
            end = l[i-1][1].split('-')[1].split(':')[0]
            start = j[1].split('-')[0].split(':')[0]
            if end > start:
                #this means that the prev class ends after the current one begins, so add both classes to conflict list
                conflicts.add(l[i-1][0])
                conflicts.add(j[0])
            elif end == start:
                #compare by minutes, get the prev end time mins and current start time mins
                end = l[i-1][1].split('-')[1].split(':')[1]
                start = j[1].split('-')[0].split(':')[1]
                if end > start:
                        conflicts.add(l[i-1][0])
                        conflicts.add(j[0])
    return conflicts

@login_required
def schedule_list(request):
    #show all of the active schedules
    schedules = Schedule.objects.filter(user__user__username=request.user.socialuser)

    return render(request, 'googleauth/schedulelist.html', {'username':request.user.socialuser, 'schedules':schedules, 'id':request.user.socialuser.id})

@login_required
def add_schedule(request):
    #set the user to be the current user
    schedule = Schedule(user=request.user.socialuser)
    if request.method == 'POST':
        sched_form = ScheduleForm(request.POST, instance = schedule)
        if sched_form.is_valid():
            sched_form.save()
            return redirect(to='schedulelist')
    else:
        sched_form = ScheduleForm(instance=schedule)
            
    return render(request, 'googleauth/addschedule.html',  {'username':request.user.socialuser, 'sched_form': sched_form})

@login_required
def delete_schedule(request, sched_id):
    sch = get_object_or_404(Schedule, pk=sched_id)
    if sch.user.id != request.user.socialuser.id:
        return redirect('schedule', sched_id=sched_id)
    Schedule.objects.filter(pk=sched_id).delete() #delete schedule
    return redirect('schedulelist')
    

@login_required
def add_class_to_schedule(request, sched_id, class_id):
    #get the schedule with the given id
    cur_sched = get_object_or_404(Schedule, pk=sched_id)
    if cur_sched.user.id != request.user.socialuser.id:
        return redirect('schedule', sched_id=sched_id)
    #get class
    class_to_add = get_object_or_404(ClassObj, pk=class_id)
    if class_to_add not in cur_sched.user.classobj_set.all():
        return redirect('schedule', sched_id=sched_id)
    #add class to schedule
    cur_sched.classes.add(class_to_add)
    #redirect to schedule
    return redirect('schedule', sched_id=sched_id)

@login_required
def remove_class_from_schedule(request, sched_id, class_id):
    #get the schedule with the given id
    cur_sched = get_object_or_404(Schedule, pk=sched_id)
    if cur_sched.user.id != request.user.socialuser.id:
        return redirect('schedule', sched_id=sched_id)
    #get class
    class_to_add = get_object_or_404(ClassObj, pk=class_id)
    if class_to_add not in cur_sched.user.classobj_set.all() or class_to_add not in cur_sched.classes.all():
        return redirect('schedule', sched_id=sched_id)
    # remove class from schedule
    cur_sched.classes.remove(class_to_add)
    #redirect to schedule
    return redirect('schedule', sched_id=sched_id)

@login_required
def schedule(request, sched_id):
    cur_sched = get_object_or_404(Schedule, pk=sched_id)
    #get all of the classes in the cur_sched
    c = cur_sched.classes.all()
    print(c)
    
    interestedClasses = cur_sched.user.classobj_set.all()
    interestedList = zip(interestedClasses, [cl.subject+" "+cl.catalog_number+"-"+cl.course_section for cl in interestedClasses])
    
    is_cur_user = cur_sched.user.id == request.user.socialuser.id
    
    following = request.user.socialuser.friends.all()
    f_ids = []
    for follower in following:
        f_ids.append(follower.socialuser.id)
        
    is_following = cur_sched.user.id in f_ids
   
    #populate dictionaries for each day of the week which should give {class name:starttime-endtime} pairing
    monday_list = {cl.subject+" "+cl.catalog_number+"-"+cl.course_section:convert_time(cl.start_time)+'-'+convert_time(cl.end_time) for cl in c if 'Mo' in cl.days}
    tuesday_list = {cl.subject+" "+cl.catalog_number+"-"+cl.course_section:convert_time(cl.start_time)+'-'+convert_time(cl.end_time) for cl in c if 'Tu' in cl.days}
    wednesday_list = {cl.subject+" "+cl.catalog_number+"-"+cl.course_section:convert_time(cl.start_time)+'-'+convert_time(cl.end_time) for cl in c if 'We' in cl.days}
    thursday_list = {cl.subject+" "+cl.catalog_number+"-"+cl.course_section:convert_time(cl.start_time)+'-'+convert_time(cl.end_time) for cl in c if 'Th' in cl.days}
    friday_list = {cl.subject+" "+cl.catalog_number+"-"+cl.course_section:convert_time(cl.start_time)+'-'+convert_time(cl.end_time) for cl in c if 'Fr' in cl.days}

    #now ensure that dictionary is in sorted order by ascending class start time
    monday_list = dict(sorted(monday_list.items(), key=lambda i: (i[1].split(':')[0], i[1].split(':')[1]) ))
    tuesday_list = dict(sorted(tuesday_list.items(), key=lambda i: (i[1].split(':')[0], i[1].split(':')[1]) ))
    wednesday_list = dict(sorted(wednesday_list.items(), key=lambda i: (i[1].split(':')[0], i[1].split(':')[1]) ))
    thursday_list = dict(sorted(thursday_list.items(), key=lambda i: (i[1].split(':')[0], i[1].split(':')[1]) ))
    friday_list = dict(sorted(friday_list.items(), key=lambda i: (i[1].split(':')[0], i[1].split(':')[1]) ))

    #find conflicting classes
    #already sorted by increasing start time
    monday_conflicts = find_conflicts(monday_list)
    tuesday_conflicts = find_conflicts(tuesday_list)
    wednesday_conflicts = find_conflicts(wednesday_list)
    thursday_conflicts = find_conflicts(thursday_list)
    friday_conflicts = find_conflicts(friday_list)
    
    comments = cur_sched.schedulecomment_set.order_by('-pub_date')

    return render(request, 'googleauth/schedule.html', {'c':c, 'interestedList':interestedList, 'monday_list':monday_list, 'tuesday_list':tuesday_list, 'wednesday_list':wednesday_list, 'thursday_list': thursday_list, 'friday_list':friday_list, 'monday_conflicts':monday_conflicts, 'tuesday_conflicts':tuesday_conflicts, 'wednesday_conflicts':wednesday_conflicts, 'thursday_conflicts':thursday_conflicts, 'friday_conflicts':friday_conflicts, 'cur_sched':cur_sched, 
    'id':request.user.socialuser.id, 'is_cur_user':is_cur_user, 'is_following':is_following, 'comments':comments})

@login_required
def delete_class(request, class_id):
    cls = get_object_or_404(ClassObj, pk=class_id)
    #get all the users that currently have the class added
    all_users = cls.susers.all().exclude(user=request.user)
    
    if request.method == 'POST':
        #go through all the schedules and remove the class from the schedule
        for sched in Schedule.objects.filter(user=request.user.socialuser):
            if cls in sched.classes.all():
                sched.classes.remove(cls)

        #this is replacing the susers with all of the users that have the class added and are not the current user
        cls.susers.set(all_users)
        #redirect back to current schedule page
        return redirect('schedule', sched_id=request.POST['cur_sched_id'])
    #if not a post request just render the schedule as usual
    return render(request, 'googleauth/schedule.html', {})


    
@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        socialuser_form = UpdateSocialUserForm(request.POST, instance=request.user.socialuser)
        
        if user_form.is_valid() and socialuser_form.is_valid():
            user_form.save()
            socialuser_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect(to='profile/'+str(request.user.socialuser.id))
    
    else:
        user_form = UpdateUserForm(instance=request.user)
        socialuser_form = UpdateSocialUserForm(instance=request.user.socialuser)
            
            
    return render(request, 'googleauth/profile.html', {'user_form': user_form, 'socialuser_form': socialuser_form, 'id':request.user.socialuser.id})

# Django - Update User Profile
# https://dev.to/earthcomfy/django-update-user-profile-33ho 

@login_required
def profile_specific(request, socialuser_id):
    try:
        socialuser = SocialUser.objects.get(pk=socialuser_id)
        user = request.user
        username = socialuser.user.username
        bio = socialuser.bio
        friends = socialuser.friends.all()
        friended_by = socialuser.user.friended_by.all()
        id_list = []
        for friend in user.socialuser.friends.all():
            id_list.append(int(friend.socialuser.id))
        schedules = socialuser.schedule_set.all()
        exists = True
        return render(request, 'googleauth/profile_2.html', {'username': username, 'bio':bio, 'friends':friends, 'friended_by':friended_by, 'exists':exists, 'user':user, 'id':socialuser_id, 'id_list':id_list, 'schedules':schedules})
    except SocialUser.DoesNotExist:
        return HttpResponseNotFound()
        user = request.user
        username = ""
        bio = ""
        friends = ""
        friended_by = ""
        id_list = ""
        exists = False
        schedules = ""
        return render(request, 'googleauth/profile_2.html', {'username': username, 'bio':bio, 'friends':friends, 'friended_by':friended_by, 'exists':exists, 'user':user, 'id':socialuser_id, 'id_list':id_list, 'schedules':schedules})

        
@login_required
def interested(request, course_name):
    mnemonic = course_name.split('-')[0]
    section = course_name.split('-')[2]
    if request.method == 'POST':
        data = requests.get('http://luthers-list.herokuapp.com/api/dept/%s/?format=json' % (mnemonic))
        classList = data.json()
        for c in classList:
            if str(c['course_number']) == section:
                #course = ClassObj.objects.get(course_number=section)
                course = ClassObj.objects.filter(course_number=section).first()
                if course is not None:
                    course = ClassObj.objects.get(course_number=section)
                    #if the current user is not in the list of users with class added, add the current user
                    if request.user.socialuser not in course.susers.all():
                        course.susers.add(request.user.socialuser)
                        course.save()
                        messages.success(request, "Added class to your interested class list.")
                    else:
                        messages.error(request, "You are already enrolled in this class!")

                else:
                    course = ClassObj(subject=c['subject'],catalog_number=c['catalog_number'],course_number=str(c['course_number']),
                                          name=c['instructor']['name'],email=c['instructor']['email'],semester_code=str(c['semester_code']),
                                          course_section=c['course_section'],description=c['description'],units=c['units'],
                                          component=c['component'],class_capacity=str(c['class_capacity']),
                                          wait_list=str(c['wait_list']),wait_cap=str(c['wait_cap']),enrollment_total=str(c['enrollment_total']),
                                          enrollment_available=str(c['enrollment_available']),topic=c['topic'],
                                          days=c['meetings'][0]['days'],start_time=c['meetings'][0]['start_time'],
                                          end_time=c['meetings'][0]['end_time'],facility_description=c['meetings'][0]['facility_description'])
                    course.save()
                    course.susers.add(request.user.socialuser)
                    course.save()
                    messages.success(request, "Added class to your interested class list.")
    return redirect('searchresults')

# @login_required
# def alreadyenrolled(request, course_name):
#     mnemonic = course_name.split('-')[0]
#     number = course_name.split('-')[1]
#     section = course_name.split('-')[2]
#     print(course_name)
#     return render(request, 'googleauth/already_enrolled.html', {'mnemonic': mnemonic, 'number': number, 'section': section})

@login_required
def search_people(request):
    # Used https://learndjango.com/tutorials/django-search-tutorial and 
    # https://docs.djangoproject.com/en/4.1/topics/db/search for object querying
    # and search tips
    search_name = request.GET.get("name")
    matches = []
    if search_name:
        social_users = SocialUser.objects.all()
        for social_user in social_users:
            username = social_user.user.username
            if search_name.lower() in username.lower():
                matches.append(social_user)

    return render(request, 'googleauth/search_people.html', {'peopleList': matches, 'search_name': search_name, 'id': request.user.socialuser.id})

@login_required
def add_friend(request,socialuser_id):
    try:
        socialuser = SocialUser.objects.get(pk=socialuser_id)
        request.user.socialuser.friends.add(socialuser.user)
        return redirect(to="../profile/"+str(socialuser_id))
    except SocialUser.DoesNotExist:
        return redirect(to="../profile/"+str(socialuser_id))
  
@login_required
def remove_friend(request,socialuser_id):
    try:
        socialuser = SocialUser.objects.get(pk=socialuser_id)
        is_friend = False
        for friend in request.user.socialuser.friends.all():
            if socialuser_id == friend.socialuser.id:
                is_friend = True
        if is_friend:
            request.user.socialuser.friends.remove(socialuser.user)
            return redirect(to="../profile/"+str(socialuser_id))
        else:
            return redirect(to="../profile/"+str(socialuser_id))
    except SocialUser.DoesNotExist:
        return redirect(to="../profile/"+str(socialuser_id))

@login_required
def add_comment(request):
    if request.method == 'POST':
        owner_id = int(request.POST['owner_id'])
        commentor_id = int(request.POST['commentor_id'])
        sched_id = int(request.POST['sched_id'])
        
        commentdata = request.POST['comment']
        owner = get_object_or_404(SocialUser,pk=owner_id)
        commentor = get_object_or_404(SocialUser,pk=commentor_id)
        scheduleobj = get_object_or_404(Schedule,pk=sched_id)
        c_name = commentor.user.username
        
        schedule_comment = ScheduleComment(schedule_owner=owner,comment_poster=commentor,schedule=scheduleobj,commentor_name=c_name,comment=commentdata,pub_date=datetime.now())
        schedule_comment.save()
        
        return redirect(to="../schedule/"+str(sched_id))
    else:
        return HttpResponseNotFound()
    
@login_required   
def delete_comment(request):
    if request.method == 'POST':
        sched_id = int(request.POST['sched_id'])
        
        comment_id = int(request.POST['comment_id'])
        comment = get_object_or_404(ScheduleComment,pk=comment_id)
        comment.delete()
        
        return redirect(to="../schedule/"+str(sched_id))
    else:
        return HttpResponseNotFound()
