from django import template
from ..models import *
from django.contrib.auth.models import User,Group
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
register = template.Library()




@register.filter
def getModel(obj):
    # print(obj._meta.model_name)
    return obj._meta.model_name


@register.filter
def getUser(value):
    users = User.objects.filter(id__in=value)
    # print(",".join(str(x) for x in list(users.values_list('username',flat=True))))

    return ",".join(str(x) for x in list(users.values_list('username',flat=True)))

@register.filter
def getUserp(value):
    users = Profile.objects.filter(user__id__in=value)
    # print(",".join(str(x) for x in list(users.values_list('username',flat=True))))

    return users
@register.filter
def getUserID(value):
    users = User.objects.filter(id__in=value)
    # print(",".join(str(x) for x in list(users.values_list('id',flat=True))))

    return ",".join(str(x) for x in list(users.values_list('id',flat=True)))



@register.filter
def getStatus(status):
    if status==1:
        return 'Waiting for admin approval'
    elif status==2:
        return 'Accepted'
    elif status==3:
        return 'Waiting for admin approval'
    # print(status)
    
@register.filter
def getStatuss(status):
    if status==1:
        return 'Pending'
    elif status==2:
        return 'Accepted'
    elif status==3:
        return 'Rejected'
    # print(status)

@register.filter
def getUserPic(userId):
    try:
        pass
        profile = Profile.objects.get(user__username=userId)
        # print(profile.profile_pic)
        return profile.profile_pic.url
    except Profile.DoesNotExist:
        return ''
@register.filter
def get_related_entity(id):

    user = User.objects.get(id=id)
    # profile =get_object_or_404(Profile,user_id=id)
    if user:
        startup = Startup.objects.filter(profile__user=user).first()
        mentor = Mentor.objects.filter(profile__user=user).first()
        iha = IncubatorsAccelatorsHub.objects.filter(profile__user=user).first()
        donor_funder = DonorFunder.objects.filter(profile__user=user).first()
        government = Government.objects.filter(profile__user=user).first()
        if startup is not None:
            return startup._meta.model.__name__
        elif mentor is not None:
            return mentor._meta.model.__name__
        elif iha is not None:
            return iha._meta.model.__name__
        elif donor_funder is not None:
            return donor_funder._meta.model.__name__
        elif government is not None:
            return government._meta.model.__name__
    else:
        # print(True)
        pass

            # return HttpResponse('user has no profile')
    # return obj._meta.model.__name__


@register.filter
def getOtherRecipent(userId,user):
    try:
        filtered_array = [x for x in userId if int(x)  != user.id]
        z=[]
        profile = Profile.objects.filter(user__id__in=filtered_array)
        for i in profile:
            z.append(i)
        return z
    except Profile.DoesNotExist:
        return ''
    
@register.filter
def isSent(recipient_ids,user):
    try:
        if user in recipient_ids:
            return False
        else:
            return True
        
    except Profile.DoesNotExist:
        return ''

@register.filter
def getName(recipient_ids):
    try:
        profile = Profile.objects.filter(user_id__in=recipient_ids)
        if profile:
            startup = list(Startup.objects.filter(profile_id__in=list(profile.values_list('id',flat=True))).values_list('profile__user__username',flat=True))
            mentor = list(Mentor.objects.filter(profile_id__in=list(profile.values_list('id',flat=True))).values_list('profile__user__username',flat=True))
            iha = list(IncubatorsAccelatorsHub.objects.filter(profile_id__in=list(profile.values_list('id',flat=True))).values_list('profile__user__username',flat=True))
            donor_funder = list(DonorFunder.objects.filter(profile_id__in=list(profile.values_list('id',flat=True))).values_list('profile__user__username',flat=True))
            government = list(Government.objects.filter(profile_id__in=list(profile.values_list('id',flat=True))).values_list('profile__user__username',flat=True))
            m=startup+mentor+iha+donor_funder+government
            result_string = ','.join(m)
            print(result_string)

            # print(m)
            return result_string

    except Profile.DoesNotExist:
        return ''
    
    
@register.filter
def getSenderPic(userId):
    try:
        profile = Profile.objects.get(user__id=userId)
        return profile.profile_pic.url
    except Profile.DoesNotExist:
        return ''
from django.db.models import Q
@register.filter
def getLatestMessage(userId):
    try:
        latest_message = Message.objects.get(id=userId)
        
        # Get the latest message for the given sender and where any recipient in latest_message.recipients
        latest_message = Message.objects.filter(
            sender=latest_message.sender,
            recipients__overlap=latest_message.recipients  # Use overlap for array matching
        ).latest('creation_date')
        
        return latest_message.message
    except Profile.DoesNotExist:
        return ''

@register.filter
def getLatestMessageTime(userId):
    try:
        latest_message = Message.objects.get(id=userId)
        latest_message = Message.objects.filter(
            sender=latest_message.sender,
            recipients__overlap=latest_message.recipients  # Use overlap for array matching
        ).latest('creation_date')
        return latest_message.creation_date
    except Profile.DoesNotExist:
        return ''
@register.filter
def getAllRelated(userId):
    try:
        latest_message = Message.objects.get(id=userId)
        latest_message = Message.objects.filter(
            sender=latest_message.sender,
             # Use overlap for array matching
        )
        return latest_message
    except Profile.DoesNotExist:
        return ''
    