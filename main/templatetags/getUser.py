from django import template
from ..models import *
from django.contrib.auth.models import User,Group
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
register = template.Library()




@register.filter
def getModel(obj):
    print(obj._meta.model_name)
    return obj._meta.model_name


@register.filter
def getUser(value):
    users = User.objects.filter(id__in=value)
    print(",".join(str(x) for x in list(users.values_list('username',flat=True))))

    return ",".join(str(x) for x in list(users.values_list('username',flat=True)))



@register.filter
def getStatus(status):
    if status==1:
        return 'Waiting for admin approval'
    elif status==2:
        return 'Accepted'
    elif status==3:
        return 'Waiting for admin approval'
    print(status)
    
@register.filter
def getStatuss(status):
    if status==1:
        return 'Pending'
    elif status==2:
        return 'Accepted'
    elif status==3:
        return 'Rejected'
    print(status)

@register.filter
def getUserPic(userId):
    try:
        profile = Profile.objects.get(user__id=userId)
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
        print(True)
        pass

            # return HttpResponse('user has no profile')
    # return obj._meta.model.__name__