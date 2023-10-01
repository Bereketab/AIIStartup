from django import template
from ..models import *
from django.contrib.auth.models import User,Group
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db.models import BooleanField
from django.db.models import Value

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
def getName(message,userId):
    try:
        profile = Profile.objects.filter(user_id__in=message.recipient_ids)
        # messages = Message.objects
        if profile:
            startup = list(Startup.objects.filter(profile_id__in=list(profile.values_list('id',flat=True))).values_list('profile__user__username',flat=True))
            mentor = list(Mentor.objects.filter(profile_id__in=list(profile.values_list('id',flat=True))).values_list('profile__user__username',flat=True))
            iha = list(IncubatorsAccelatorsHub.objects.filter(profile_id__in=list(profile.values_list('id',flat=True))).values_list('profile__user__username',flat=True))
            donor_funder = list(DonorFunder.objects.filter(profile_id__in=list(profile.values_list('id',flat=True))).values_list('profile__user__username',flat=True))
            government = list(Government.objects.filter(profile_id__in=list(profile.values_list('id',flat=True))).values_list('profile__user__username',flat=True))
            m=startup+mentor+iha+donor_funder+government
            userName=User.objects.get(id=userId).username
            for i in m:
                if i==userName:
                    m.remove(userName)
                    m.append(str(message.sender))
            # print(m.remove(str(userName)))
                    # print(type(userName))
            result_string = ','.join(m)
            
            # print(type(profile))

            # print(User.objects.get(id=userId).username)
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
def getAllRelated(conversationId,userId):
    # print(conversationId)
    try:
        message = Message.objects.filter(conversation=conversationId)
        message_sent = message.filter(sender=userId).annotate(is_sent=Value(True, output_field=BooleanField()))
        message_recive = message.exclude(sender=userId).annotate(is_sent=Value(False, output_field=BooleanField()))
        merged = message_recive.union(message_sent)
        return merged.order_by('-timestamp')
    except Profile.DoesNotExist:
        return ''

@register.filter
def getLatestMessageTime(conversationId,userId):
    try:
        timestamp = Message.objects.filter(conversation=conversationId).order_by('-timestamp').first().timestamp
        return timestamp

    except Profile.DoesNotExist:
        return ''
from django.contrib.postgres.aggregates import ArrayAgg
# @register.filter
# def getAllRelated(userId):
#     try:
#         latest_message=Message.objects.annotate(recipient_ids=ArrayAgg("recipients"))
#         latest_message1 = latest_message.get(id=userId)
#         latest_message2 = latest_message.filter(
#             sender=latest_message1.sender,
#             recipient_ids=sorted(latest_message1.recipient_ids)
#         )
#         latest_message3 = latest_message.filter(
#             sender_id__in=sorted(latest_message1.recipient_ids),
#         )
#         return latest_message3.filter(recipient_ids=sorted(latest_message1.recipient_ids)).union(latest_message2)
#     except Profile.DoesNotExist:
#         return ''
    
# @register.filter
# def isSender(message,userId):
#     try:
#         latest_message=Message.objects.annotate(recipient_ids=ArrayAgg("recipients"))
#         latest_message2 = latest_message.get(id=message)
#         # if(latest_message2.)
#         # latest_message2 = latest_message.filter(
#         #     sender=latest_message2.sender,
#         #     recipient_ids=sorted(latest_message2.recipient_ids)
#         # )
#         return latest_message2.sender.id==userId
#     except Profile.DoesNotExist:
#         return ''
    
    
    
from aii_startup import settings
@register.filter
def getV(value):
    print(value)
    return True

@register.filter
def getRecipentImage(cId,uId):
    c=Conversation.objects.get(id=cId)
    profile = Profile.objects.filter(id__in=sorted(list(c.participants.values_list('id',flat=True)))).exclude(user_id=uId)
    media_url = settings.MEDIA_URL  # Make sure 'settings' is imported
    paths=list(profile.values_list('profile_pic',flat=True))
    usernames,pic = list(profile.values_list('user__username','profile_pic'))
    
    # print(usernames)
    # print(pic)
    # recipient_images = [f"{media_url}{path}" for path in paths]
    
    return {'src':[f"{media_url}{path}" for path in paths],'username':usernames}

