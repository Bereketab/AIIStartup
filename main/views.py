from .models import *
from .forms import *
from django.db.models import *
from django.contrib.auth.models import User,Group
from django.db import DatabaseError, transaction
from django.contrib.auth import logout
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.shortcuts import render,redirect
from .forms import *
from .view_logic import *
from django.shortcuts import render, get_object_or_404
import json
from operator import or_
from functools import reduce
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib import messages

context = {}





def checkProfileType(user):
    if len(Startup.objects.filter(profile__user=user.id))>=1:
        return 'Startup'
    if len(Mentor.objects.filter(profile__user=user.id))>=1:
        return 'Mentor'
    if len(IncubatorsAccelatorsHub.objects.filter(profile__user=user.id))>=1:
        return 'Incubators/Accelators/Hub'
    if len(DonorFunder.objects.filter(profile__user=user.id))>=1:
        return 'Donor/Funder'
    if len(Government.objects.filter(profile__user=user.id))>=1:
        return 'Government'
    
STATUS_CHOICES = (
        (1, 'Pending'),
        (2, 'Accepted'),
        (3, 'Rejected'),
    )
def getFilteredOf(objectT,request,connect):
    objectT=objectT.annotate(
             is_connected=Case(
             When(
             Exists(
             Subquery(  
             connect.filter(
                  Q(requester=OuterRef('profile__user'),responser=request.user.id) |
                     Q(responser=OuterRef('profile__user'),requester=request.user.id)
             ).values_list('status',flat=True))),
             then=connect.filter(
                  Q(requester=OuterRef('profile__user'),responser=request.user.id) |
                     Q(responser=OuterRef('profile__user'),requester=request.user.id)
             ).values_list('status',flat=True)
             ),
             default=Value(0)
             )
        )
    return objectT

from uuid import uuid4

@login_required(login_url='/login/')
def logged_user(request):
    if request.user.is_authenticated and  not request.user.is_superuser:
        current_profile = Profile.objects.get(user=request.user.id)
        context['profile_type']=current_profile
        context['connect'] = Connect.objects.filter(Q(responser=request.user.id) | Q(requester=request.user.id))
        context['startups'] = Startup.objects.exclude(profile__user=request.user.id)
        context['startups']= getFilteredOf(context['startups'],request,context['connect'])
        context['mentors'] = Mentor.objects.exclude(profile__user=request.user.id)
        context['iah'] = IncubatorsAccelatorsHub.objects.exclude(profile__user=request.user.id)
        context['df'] = DonorFunder.objects.exclude(profile__user=request.user.id)
        context['government'] = Government.objects.exclude(profile__user=request.user.id)
        context['mentors']=  getFilteredOf(context['mentors'],request,context['connect'])
        context['iah']= getFilteredOf(context['iah'],request,context['connect'])
        context['df']=  getFilteredOf(context['df'],request,context['connect'])
        context['government']=  getFilteredOf(context['government'],request,context['connect'])
        return render (request,'logged_user/index.html',context)
    else:
         return HttpResponse("unauthorized user please login in correct profile ")


def saveContact(request):
    if request.method == "POST":
        try:
            poster = Poster(
                name=request.POST['name'],
                email=request.POST['email'],
                subject=request.POST['subject'],
                message=request.POST['message'],
                disabled=False,
            )
            poster.save()
            messages.success(request, "you request have been submitted successfully!")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
    
    return redirect('main:home')


def contacted_list(request):
    contacted = Poster.objects.all() 
    context['contacted']=contacted
    return render(request,'adminstration/contacted.html',context)

@login_required
def messagess(request):
    message = Message.objects.filter(sender=request.user)
    for w in Message.objects.all():
         for ww in w.recipients:
              if(str(ww)==str(request.user.id)):
                   xx=Message.objects.filter(id=w.id)
    context['chats'] = xx|message
    context['chats']=context['chats'].order_by('recipients','creation_date').reverse().distinct('recipients')
    return render(request, "messages/message.html",context)

def currentUserConnectUserList(request):
    if request.method == 'POST':
        user_id = request.POST.get('user')  # Assuming you're sending the user's ID in the POST data
        
        if request.user.is_authenticated and request.user.id == int(user_id):
            connected_profiles = Connect.objects.filter(status_admin=2)
            connected_profiles =connected_profiles.filter(Q(requester=request.user)|Q(responser=request.user))
            connected_profiles = connected_profiles.filter(status=2).values_list('responser__profile', flat=True)
            connected_profiles = list(connected_profiles) + list(Connect.objects.filter(responser=request.user, status=2,status_admin=2).values_list('requester__profile', flat=True))
            
            connected_entities = list(
                Startup.objects.filter(profile__in=connected_profiles).exclude(profile__user=request.user).values('profile__user__username',"profile__user__id")) + \
                list(Mentor.objects.filter(profile__in=connected_profiles).exclude(profile__user=request.user).values('profile__user__username',"profile__user__id")) + \
                list(IncubatorsAccelatorsHub.objects.filter(profile__in=connected_profiles).exclude(profile__user=request.user).values('profile__user__username',"profile__user__id")) + \
                list(DonorFunder.objects.filter(profile__in=connected_profiles).exclude(profile__user=request.user).values('profile__user__username',"profile__user__id")) + \
                list(Government.objects.filter(profile__in=connected_profiles).exclude(profile__user=request.user).values('profile__user__username',"profile__user__id"))
    
            return JsonResponse(connected_entities,safe=False)
            # return JsonResponse({'connected_entities': serialized_entities})
        else:
            return JsonResponse({'error': 'Invalid user or not authenticated'})
    else:
        return JsonResponse({'error': 'Invalid request method'})


import uuid
from django.db.models import OuterRef, Subquery
def messagess(request):
    socket_session=uuid.uuid4()
    m = Message.objects.all()
    context['messages_sent_d'] = m
   
    return render(request, 'logged_user/messages.html',context)

import ast
def sentMessage(request):
    if request.method == "POST":
        recipient_ids = [int(i) for i in ast.literal_eval(request.POST['recievers'])]
        content = request.POST['message']
        subject=request.POST['subject']
        
        # Create a new conversation or find an existing one with the same participants
        conversation, created = Conversation.objects.get_or_create(subject=request.POST['subject'])
        conversation.participants.set(recipient_ids + [request.user.id])

        # Create a new message and associate it with the conversation and sender
        message = Message(conversation=conversation, sender=request.user, content=content)
        message.save()

        
        return render(request, 'messages/after_sent.html',context)


def conversations(request):
    user = request.user
    conversations = Conversation.objects.filter(participants=user).order_by('pk').distinct()

    # For each conversation, get the latest message and attach it to the conversation
    for conversation in conversations:
        latest_message = Message.objects.filter(conversation=conversation).latest('timestamp')
        
        conversation.latest_message = latest_message
    
    context = {
        'conversations': conversations
    }
    # print(conversations.order_by('pk').values())


    return render(request, 'messages/sent.html',context)
import ast
def sentMessagefromDetail(request):
    if request.method=="POST":
        conversationId=request.POST['conversationId']
        content = request.POST['message']
        conversation, created = Conversation.objects.get_or_create(id=conversationId)

        # Create a new message and associate it with the conversation and sender
        message = Message(conversation=conversation, sender=request.user, content=content)
        message.save()
        return render(request, 'messages/after_sent.html',context)



from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def message_detail(request, messageId):
    current_message=Message.objects.get(id=messageId)
    sender_condition = Q(sender=current_message.sender)
    recipients_condition = Q(recipients__contains=current_message.recipients)
    
    # Combine the conditions using the & operator for AND
    related_message = Message.objects.filter(sender_condition & recipients_condition)
    print(related_message)
    context = {'detail_message': related_message}
    
    return render(request, 'messages/message-detail.html', context)

def admin(request):
    if request.user.is_authenticated and request.user.is_superuser:
         return render(request, 'adminstration/index.html')
    else:
         return render(request, 'main/login.html')

def c_connected(request):
     my_connect = Connect.objects.filter(Q(requester=request.user)|Q(responser=request.user))
     my_connect=my_connect.filter(status=2,status_admin=2)
     context['connect']=my_connect
    #  print(my_connect)
     return render(request, 'connected/connected.html',context)
def c_sent(request):
     my_connect = Connect.objects.filter(Q(requester=request.user))
     my_connect=my_connect.filter(~Q(status=2) | ~Q(status_admin=2))
     context['connect']=my_connect
     return render(request, 'connected/sent.html',context)
def c_recived(request):
     my_connect = Connect.objects.filter(Q(responser=request.user))
     my_connect=my_connect.filter(~Q(status=2) | ~Q(status_admin=2))
     context['connect']=my_connect
     return render(request, 'connected/recived.html',context)
def accept(request,pk):
    return_to = request.GET.get('return_to')

    my_connect = Connect.objects.filter(id=pk)
    my_connect.update(status=2)
    context['connect']=my_connect
    if return_to:
        return redirect(return_to)
def adminLogin(request):
     return render(request,'adminstration/login.html')


def get_model_name(instance):
    return instance._meta.model_name


def profile_list(request):
    startups = Startup.objects.all()
    mentor = Mentor.objects.all()
    incubatorsAccelatorsHub = IncubatorsAccelatorsHub.objects.all()
    donorFunder= DonorFunder.objects.all()
    government = Government.objects.all()
    context['startups'] =startups
    context['mentors'] =mentor
    context['incubatorsAccelatorsHub'] =incubatorsAccelatorsHub
    context['donorFunder'] =donorFunder
    context['government'] =government    
    merged_objects = list(startups) + list(mentor) + list(incubatorsAccelatorsHub) + list(donorFunder) + list(government)
    context ['merged_objects']= merged_objects
    return render(request,'adminstration/profile_list.html',context)

def activate_profile(request, id):
    user1 = User.objects.filter(id=id)
    user1.update(is_active=True)
    # print(user1)
    startups = Startup.objects.all()
    mentor = Mentor.objects.all()
    incubatorsAccelatorsHub = IncubatorsAccelatorsHub.objects.all()
    donorFunder= DonorFunder.objects.all()
    government = Government.objects.all()
    context['startups'] =startups
    context['mentor'] =mentor
    context['incubatorsAccelatorsHub'] =incubatorsAccelatorsHub
    context['donorFunder'] =donorFunder
    context['government'] =government    
    return HttpResponseRedirect(reverse('main:profile_list'))
def decativate_profile(request, id):
    user1 = User.objects.filter(id=id)
    user1.update(is_active=False)
    # print(user1)
    startups = Startup.objects.all()
    mentor = Mentor.objects.all()
    incubatorsAccelatorsHub = IncubatorsAccelatorsHub.objects.all()
    donorFunder= DonorFunder.objects.all()
    government = Government.objects.all()
    context['startups'] =startups
    context['mentor'] =mentor
    context['incubatorsAccelatorsHub'] =incubatorsAccelatorsHub
    context['donorFunder'] =donorFunder
    context['government'] =government    
    return HttpResponseRedirect(reverse('main:profile_list'))

def connection_list(request):
     context['connect'] = Connect.objects.all()
     return render(request,'adminstration/connection_list.html',context)

def message_list(request):
     context['message'] = Message.objects.all()
     return render(request,'adminstration/message_list.html',context)

def m_compose(request):
     return render(request, 'messages/compose.html')
from django.db.models import BooleanField, Value
from django.db.models import F
from collections import defaultdict
from django.db.models import BooleanField, Value, Count
from django.contrib.postgres.fields import ArrayField
import datetime
from django.contrib.postgres.aggregates import ArrayAgg

# def m_inbox(request):
#     my_message = Message.objects.all()
#     i_send = my_message.filter(sender=request.user)
#     i_receive = my_message.filter(recipients=request.user)   
#     i_send = i_send.annotate(recipient_ids=ArrayAgg("recipients"))
#     def getLatestISend( x):
#         count = 0
#         v=[]
#         for ele in i_send:
#             if (sorted(ele.recipient_ids)==sorted(list(x))):
#                 v.append({'creation_date':ele.creation_date,'id':ele.id})
#         count = max(list(x for x in v), key=lambda x: x['creation_date'])
#         return count
    
#     grouped_messages_i_send = []
#     grouped_messages_i_recive = []
#     for message_data in i_send:
#         recipient_ids_tuple = tuple(sorted(message_data.recipient_ids))
#         grouped_messages_i_send.append(getLatestISend(recipient_ids_tuple))
#     i_send=i_send.filter(pk__in=sorted(list(set([e['id'] for e in grouped_messages_i_send]))))
#     i_receive=my_message.filter(id__in=list(i_receive.values_list('id',flat=True))).annotate(recipient_ids=ArrayAgg("recipients"))
    
#     def getLatestIRecive( x):
#         count = 0
#         v=[]
#         for ele in i_receive:
#             if (sorted(ele.recipient_ids)==sorted(list(x))):
#                 v.append({'creation_date':ele.creation_date,'id':ele.id})
#         count = max(list(x for x in v), key=lambda x: x['creation_date'])
#         return count
#     for message_data in i_receive:
#         recipient_ids_tuple = message_data.recipient_ids
#         grouped_messages_i_recive.append(getLatestIRecive(recipient_ids_tuple))
#     i_receive=i_receive.filter(pk__in=sorted(list(set([e['id'] for e in grouped_messages_i_recive]))))
#     merged=my_message.filter(sender=request.user).values('creation_date').annotate(
#     recipient_ids=ArrayAgg('recipients')
# ).order_by('-creation_date')| my_message.filter(recipients=request.user).values('creation_date').annotate(
#     recipient_ids=ArrayAgg('recipients')
# ).order_by('-creation_date')   

    
    
#     context['my_inbox']=merged
#     print(merged.values())
#     return render(request, 'messages/sent.html',context)

@csrf_exempt
def getDetail(request):
    if request.method=="POST":
        conversationId = request.POST['conversationID']
        
        message = Message.objects.filter(conversation=conversationId)
        message_sent = message.filter(sender_id=request.user.id).annotate(is_sent=Value(True, output_field=BooleanField()))
        message_recive = message.exclude(sender_id=request.user.id).annotate(is_sent=Value(False, output_field=BooleanField()))
        merged = message_recive.union(message_sent)
        context['messages']=merged.order_by('timestamp')
        print(merged.values())

        
        return render(request,'messages/message-detail.html',context)

def m_outbox(request):
    my_outbox = Message.objects.filter(~Q(recipients= request.user) )
    my_outbox = Message.objects.filter(sender=request.user)
    context['my_outbox']=my_outbox.distinct('recipients')
    return render(request, 'messages/recived.html',context)

from rest_framework.authtoken.models import Token
def loginUser(request):
    if request.method== 'POST':
        login_request = request.POST
        username = login_request.get('username')
        password = login_request.get('password')
        user = authenticate(request, username=username, password=password)
        if not login_request.get('admin')=="on":
            if user and user.is_active:
                login(request, user)
            else:
                 return HttpResponse("not active user or registered user")
            return HttpResponseRedirect(reverse('main:home'))
        if login_request.get('admin')=="on":
            login(request, user)
            return HttpResponseRedirect(reverse('main:admin'))
        
         
          
       
   
    else:
            return render (request,'main/login.html',context)
from django.core import serializers   
def homePage(request):
    context['startup'] = Startup.objects.filter(profile__user__is_active=True)
    context['mentor'] = Mentor.objects.filter(profile__user__is_active=True)
    context['incubator'] = IncubatorsAccelatorsHub.objects.filter(profile__user__is_active=True)
    context['investor'] = DonorFunder.objects.filter(profile__user__is_active=True)
    context['government'] = Government.objects.filter(profile__user__is_active=True)
    merged_objects = list(context['startup']) + list(context['mentor']) + list(context['incubator']) + list(context['investor']) + list(context['government'] )
    data = serializers.serialize('json', merged_objects)
    context['merged_objects']=merged_objects

    return render (request,'main/index.html',context)


def explore(request):
    if request.user.is_authenticated and  not request.user.is_superuser:
        current_profile = Profile.objects.get(user=request.user.id)
        context['profile_type']=current_profile
        context['connect'] = Connect.objects.filter(Q(responser=request.user.id) | Q(requester=request.user.id))
        context['startups'] = Startup.objects.exclude(profile__user=request.user.id)
        user = User.objects.prefetch_related('requester').prefetch_related('responser').values_list('id',flat=True)
        context['mentors'] = Mentor.objects.exclude(profile__user=request.user.id)
        context['iah'] = IncubatorsAccelatorsHub.objects.exclude(profile__user=request.user.id)
        context['df'] = DonorFunder.objects.exclude(profile__user=request.user.id)
        context['government'] = Government.objects.exclude(profile__user=request.user.id)
        context['startups']= getFilteredOf(context['startups'],request,context['connect'])
        context['mentors']=  getFilteredOf(context['mentors'],request,context['connect'])
        context['iah']= getFilteredOf(context['iah'],request,context['connect'])
        context['df']=  getFilteredOf(context['df'],request,context['connect'])
        context['government']=  getFilteredOf(context['government'],request,context['connect'])
        
        
        return render (request,'logged_user/index.html',context)
    else:
        logout(request)
        return HttpResponseRedirect(reverse('main:login'))
    


@login_required(login_url='/login/')
def profile(request, pk):
    # print()
    return_to = request.GET.get('return_to')
    profile = Profile.objects.get(user__id=pk)
    context = {}
    redirect_base_url = reverse('main:profile', args=[pk])


    entity_mapping = {
        'Startup': (Startup, StartupForm),
        'Mentor': (Mentor, MentorForm),
        'IncubatorsAccelatorsHub': (IncubatorsAccelatorsHub, IncubatorsAccelatorsHubForm),
        'DonorFunder': (DonorFunder, DonerFunderForm),
        'Government': (Government, GovernmentForm),
    }
    if request.method == 'GET':
        if return_to in entity_mapping:
            entity_model, entity_form = entity_mapping[return_to]
            entity_instance = entity_model.objects.filter(profile=profile).first()

            if entity_instance:
                profile = Profile.objects.filter(id=entity_instance.profile.pk).first()
                user = User.objects.filter(id=profile.user.id).first()
                user_form = UserEditForm(instance=user)
                address = Address.objects.filter(id=entity_instance.address.id).first()
                address_form = AddressForm(instance=address)
                wereda = Wereda.objects.filter(id=address.location.id).first()
                region = EthRegion.objects.filter(id=wereda.region.id).first()
                description = Description.objects.filter(id=entity_instance.description.id).first()
                description_form = DescriptionForm(instance=description)
                region_form = RegionEditForm(instance=region)
                wereda_form = WeredaEditForm(instance=wereda)
                profile_form = ProfileEditForm(instance=profile)
                entity_form_instance = entity_form(instance=entity_instance)

                context['form'] = entity_form_instance
                context['profile_form'] = profile_form
                context['user_form'] = user_form
                context['address_form'] = address_form
                context['wereda_form'] = wereda_form
                context['region_form'] = region_form
                context['description_form'] = description_form
                context['typeOf'] = return_to

                return render(request, 'logged_user/edit_entity.html', context)

         
    # ... (previous code)

    if request.method == 'POST':

        entity_model, entity_form = entity_mapping[return_to]
        entity_instance = entity_model.objects.filter(profile=profile).first()
        user = User.objects.filter(id=profile.user.id).first()  # Move this line here to define 'user'

        if entity_instance:
            redirect_url = f"{redirect_base_url}?return_to={return_to}"
            # Get the forms from the POST data
            entity_form_instance = entity_form(request.POST, instance=entity_instance)
            user_form = UserEditForm(request.POST, instance=user)
            address = Address.objects.filter(id=entity_instance.address.id).first()
            wereda = Wereda.objects.filter(id=address.location.id).first()
            region = EthRegion.objects.filter(id=wereda.region.id).first()
            description = Description.objects.filter(id=entity_instance.description.id).first()
            profile = Profile.objects.filter(id=entity_instance.profile.pk).first()

            address_form = AddressForm(request.POST, instance=address)
            wereda_form = WeredaEditForm(request.POST, instance=wereda)
            region_form = RegionEditForm(request.POST, instance=region)
            description_form = DescriptionForm(request.POST, instance=description)
            profile_form =ProfileEditForm(request.POST,instance=profile)
            
            # Check if all forms are valid
            if (
                entity_form_instance.is_valid() and
                user_form.is_valid() and
                address_form.is_valid() and
                wereda_form.is_valid() and
                region_form.is_valid() and
                description_form.is_valid()
            ):
                # Save the updated forms
                entity_form_instance.save()
                user_form.save()
                address_form.save()
                wereda_form.save()
                region_form.save()
                description_form.save()
                
                # Redirect to the home page with a success message
                messages.success(request, "Profile updated successfully!")
                context['form'] = entity_form_instance
                context['profile_form'] = profile_form
                context['user_form'] = user_form
                context['address_form'] = address_form
                context['wereda_form'] = wereda_form
                context['region_form'] = region_form
                context['description_form'] = description_form
                context['typeOf'] = return_to
                messages.info(request, 'profile updated successfully!!!')

                return render(request, 'logged_user/edit_entity.html', context)
            else:
                # Handle validation errors and exceptions
                error_messages = []
                error_messages.append("Validation errors occurred. Please check the form.")
                
                # Loop through form errors and append to error_messages
                for field, errors in entity_form_instance.errors.items():
                    error_messages.append("Error in field {}: {}".format(field, errors))
                
                for field, errors in user_form.errors.items():
                    error_messages.append("Error in field {}: {}".format(field, errors))
                
                for field, errors in address_form.errors.items():
                    error_messages.append("Error in field {}: {}".format(field, errors))
                
                for field, errors in wereda_form.errors.items():
                    error_messages.append("Error in field {}: {}".format(field, errors))
                
                for field, errors in region_form.errors.items():
                    error_messages.append("Error in field {}: {}".format(field, errors))
                
                for field, errors in description_form.errors.items():
                    error_messages.append("Error in field {}: {}".format(field, errors))
                messages.success(request, error_messages)
                context['form'] = entity_form_instance
                context['profile_form'] = profile_form
                context['user_form'] = user_form
                context['address_form'] = address_form
                context['wereda_form'] = wereda_form
                context['region_form'] = region_form
                context['description_form'] = description_form
                context['typeOf'] = return_to

                return render(request, 'logged_user/edit_entity.html', context)
    return redirect('main:home')


            

         
         
   
def users_list(request):
	users = Profile.objects.exclude(user=request.user)
	context = {
		'users': users
	}
	return render(request, "startup/admin/user_list.html", context)


def connect_list(request):
	p = Profile.objects.filter(user=request.user).first()
	u = p.user
	sent_friend_requests = Connect.objects.filter(requester=request.user)
	rec_friend_requests = Connect.objects.filter(responser=request.user)

	friends = p.friends.all()

	# is this user our friend
	button_status = 'none'
	if p not in request.user.profile.friends.all():
		button_status = 'not_friend'

		# if we have sent him a friend request
		if len(Connect.objects.filter(
			requester=request.user).filter(responser=p.user)) == 1:
				button_status = 'friend_request_sent'

	context = {
		'u': u,
		'button_status': button_status,
		'friends_list': friends,
		'sent_friend_requests': sent_friend_requests,
		'rec_friend_requests': rec_friend_requests
	}
	return render(request, "startup/admin/connect_list.html", context)


def cancel_friend_request(request, id):
		user = get_object_or_404(User, id=id)
		frequest = Connect.objects.filter(
			requester=request.user,
			responser=user).first()
		frequest.delete()
		return HttpResponseRedirect('/users')

def accept_friend_request(request, id):
	requester = get_object_or_404(User, id=id)
	frequest = Connect.objects.filter(requester=requester, responser=request.user).first()
	user1 = frequest.responser
	user2 = requester
	user1.profile.friends.add(user2.profile)
	user2.profile.friends.add(user1.profile)
	frequest.delete()
	return HttpResponseRedirect('/users/{}'.format(request.user.profile.id))

def delete_friend_request(request, id):
    requester = get_object_or_404(User, id=id)
    frequest = Connect.objects.filter(requester=requester, responser=request.user).first()
    frequest.delete()
    return HttpResponseRedirect('/users/{}'.format(request.user.profile.id))

def cancel(request, pk):
    return_to = request.GET.get('return_to')
    connect = get_object_or_404(Connect, id=pk)
    connect.delete()
    if return_to:
        return redirect(return_to)

def cancel_admin(request, pk):
    return_to = request.GET.get('return_to')
    
    try:
        connect = Connect.objects.get(id=pk)
        connect.status_admin = 3  # Set the status_admin to "Rejected"
        connect.save()  # Save the changes
    except Connect.DoesNotExist:
         pass
        # Handle the case where the Connect instance doesn't exist
    
    if return_to:
        return redirect(return_to)



def active_admin(request, pk):
    return_to = request.GET.get('return_to')
    
    try:
        connect = Connect.objects.get(id=pk)
        connect.status_admin = 2  # Set the status_admin to "Rejected"
        connect.save()  # Save the changes
    except Connect.DoesNotExist:
         pass
        # Handle the case where the Connect instance doesn't exist
    
    if return_to:
        return redirect(return_to)
  

def connect_list_view(request, pk=None):
	u = User.objects.get(pk=pk)
	p = u.profile
	
	sent_friend_requests = Connect.objects.filter(requester=p.user)
	rec_friend_requests = Connect.objects.filter(responser=p.user)

	friends = p.friends.all()

	# is this user our friend
	button_status = 'none'
	if p not in request.user.profile.friends.all():
		button_status = 'not_friend'

		# if we have sent him a friend request
		if len(Connect.objects.filter(
			requester=request.user).filter(responser=p.user)) == 1:
				button_status = 'friend_request_sent'

	context = {
		'u': u,
		'button_status': button_status,
		'friends_list': friends,
		'sent_friend_requests': sent_friend_requests,
		'rec_friend_requests': rec_friend_requests
	}

	return render(request, "startup/admin/connect_list.html", context)


def send_friend_request(request, id):
		user = get_object_or_404(User, id=id)
		frequest, created = Connect.objects.get_or_create(
			requester=request.user,
			responser=user)
		return HttpResponseRedirect('/users')


@login_required(login_url='/login/')
def connect(request):
    print(request.POST)
    user = get_object_or_404(User, id=request.POST.get('userId'))
    previuosly_connected = Connect.objects.filter(Q(requester=user)).filter( Q(responser=request.user))
    if not previuosly_connected:
        try:
            frequest, created = Connect.objects.get_or_create(
                requester=request.user,
                responser=user)
        except Exception as e:
            print(e)
    else:
         print('already connected')   
    return HttpResponse('users')

def networks(request,typeOf):
    filters=[]
    if(typeOf=='startup'):
        for field in Startup._meta.get_fields(include_parents=False):
            if isinstance(field, models.OneToOneField):
                if field.name=='description':
                        for f in field.related_model._meta.get_fields(include_parents=False):
                            if( str(f.name) ==  'name' or str(f.name)=='sector'):
                                filters.append(f.verbose_name)
                if field.name=='address':
                        for f in field.related_model._meta.get_fields(include_parents=False):
                            if( str(f.name) ==  'location' ):
                                filters.append('Address')
                                        
            else:  
                if(not field.verbose_name ==  'ID'):
                    filters.append(field.verbose_name)
                    context['filters'] = filters    
        context['connect'] = Connect.objects.filter(Q(responser=request.user.id) | Q(requester=request.user.id))
        context['startups'] = Startup.objects.exclude(Q(profile__user=request.user.id) )
        context['startups']= getFilteredOf(context['startups'],request,context['connect'])

        if request.user.is_authenticated:
            connectList = Connect.objects.filter(Q(responser=request.user.id)|Q(requester=request.user.id))
            context['connectList']=connectList
            return render(request,'main/startup.html', context)
        else:
            connectList = Connect.objects.exclude(responser=request.user.id,requester=request.user.id)
            context['connect'] = Connect.objects.filter(Q(responser=request.user.id) | Q(requester=request.user.id))
            context['startups'] = Startup.objects.filter(profile__user__is_active=True).exclude(profile__user=request.user.id)
            context['startups']= getFilteredOf(context['startups'],request,context['connect'])

            return render(request,'main/startup.html', context)
    if(typeOf=='mentor'):
        for field in Mentor._meta.get_fields(include_parents=False):
            if isinstance(field, models.OneToOneField):
                if field.name=='description':
                        for f in field.related_model._meta.get_fields(include_parents=False):
                            if( str(f.name) ==  'name' or str(f.name)=='sector'):
                                filters.append(f.verbose_name)
                if field.name=='address':
                        for f in field.related_model._meta.get_fields(include_parents=False):
                            if( str(f.name) ==  'location' ):
                                filters.append('Address')                      
            else:  
                if(not field.verbose_name ==  'ID' and not field.name == 'educational_level_other' and not field.name == 'educational_background_other' and not field.name == "mentor_area_other" and not field.name == "attachments"):
                    filters.append(field.verbose_name)
                    context['filters'] = filters  
        context['connect'] = Connect.objects.filter(Q(responser=request.user.id) | Q(requester=request.user.id))
        context['mentors'] = Mentor.objects.exclude(Q(profile__user=request.user.id) )
        context['mentors']= getFilteredOf(context['mentors'],request,context['connect'])
        if request.user.is_authenticated:
            connectList = Connect.objects.filter(Q(responser=request.user.id)|Q(requester=request.user.id))
            context['connectList']=connectList
            return render(request,'main/mentor.html', context)
        else:
            connectList = Connect.objects.exclude(responser=request.user.id,requester=request.user.id)
            context['connect'] = Connect.objects.filter(Q(responser=request.user.id) | Q(requester=request.user.id))
            context['mentors'] = Mentor.objects.filter(profile__user__is_active=True).exclude(profile__user=request.user.id)
            context['mentors']= getFilteredOf(context['mentors'],request,context['connect'])

        return render(request,'main/mentor.html', context)
    if(typeOf=='incubator'):
        for field in IncubatorsAccelatorsHub._meta.get_fields(include_parents=False):
            if isinstance(field, models.OneToOneField):
                if field.name=='description':
                        for f in field.related_model._meta.get_fields(include_parents=False):
                            if( str(f.name) ==  'name' or str(f.name)=='sector'):
                                filters.append(f.verbose_name)
                if field.name=='address':
                        for f in field.related_model._meta.get_fields(include_parents=False):
                            if( str(f.name) ==  'location' ):
                                filters.append('Address')                      
            else:  
                if(not field.verbose_name ==  'ID' and not field.name == 'ownership_other' and not field.name == 'funded_by_other'   and not field.name == "attachments" and not field.name == "focusIndustry"):
                    filters.append(field.verbose_name)
                    context['filters'] = filters
        context['connect'] = Connect.objects.filter(Q(responser=request.user.id) | Q(requester=request.user.id))
        context['iah'] = IncubatorsAccelatorsHub.objects.exclude(Q(profile__user=request.user.id) )
        context['iah']= getFilteredOf(context['iah'],request,context['connect'])
        if request.user.is_authenticated:
            connectList = Connect.objects.filter(Q(responser=request.user.id)|Q(requester=request.user.id))
            context['connectList']=connectList
            return render(request,'main/iah.html', context)
        else:
            connectList = Connect.objects.exclude(responser=request.user.id,requester=request.user.id)
            context['connect'] = Connect.objects.filter(Q(responser=request.user.id) | Q(requester=request.user.id))
            context['iah'] = IncubatorsAccelatorsHub.objects.filter(profile__user__is_active=True).exclude(profile__user=request.user.id)
            context['iah']= getFilteredOf(context['iah'],request,context['connect'])

        return render(request,'main/iah.html', context)
    if(typeOf=='incub'):
        for field in IncubatorsAccelatorsHub._meta.get_fields(include_parents=False):
            if isinstance(field, models.OneToOneField):
                if field.name=='description':
                        for f in field.related_model._meta.get_fields(include_parents=False):
                            if( str(f.name) ==  'name' or str(f.name)=='sector'):
                                filters.append(f.verbose_name)
                if field.name=='address':
                        for f in field.related_model._meta.get_fields(include_parents=False):
                            if( str(f.name) ==  'location' ):
                                filters.append('Address')                      
            else:  
                if(not field.verbose_name ==  'ID' and not field.name == 'ownership_other' and not field.name == 'funded_by_other'   and not field.name == "attachments" and not field.name == "focusIndustry"):
                    filters.append(field.verbose_name)
                    context['filters'] = filters
        context['connect'] = Connect.objects.filter(Q(responser=request.user.id) | Q(requester=request.user.id))
        context['iah'] = IncubatorsAccelatorsHub.objects.exclude(Q(profile__user=request.user.id) ).filter(service='Incubation')
        context['iah']= getFilteredOf(context['iah'],request,context['connect'])
        if request.user.is_authenticated:
            connectList = Connect.objects.filter(Q(responser=request.user.id)|Q(requester=request.user.id))
            context['connectList']=connectList
            return render(request,'main/iah.html', context)
        else:
            connectList = Connect.objects.exclude(responser=request.user.id,requester=request.user.id)
            context['connect'] = Connect.objects.filter(Q(responser=request.user.id) | Q(requester=request.user.id)).filter(service='Incubation')
            context['iah'] = IncubatorsAccelatorsHub.objects.filter(profile__user__is_active=True).exclude(profile__user=request.user.id)
            context['iah']= getFilteredOf(context['iah'],request,context['connect'])

        return render(request,'main/iah.html', context)
    if(typeOf=='hub'):
        for field in IncubatorsAccelatorsHub._meta.get_fields(include_parents=False):
            if isinstance(field, models.OneToOneField):
                if field.name=='description':
                        for f in field.related_model._meta.get_fields(include_parents=False):
                            if( str(f.name) ==  'name' or str(f.name)=='sector'):
                                filters.append(f.verbose_name)
                if field.name=='address':
                        for f in field.related_model._meta.get_fields(include_parents=False):
                            if( str(f.name) ==  'location' ):
                                filters.append('Address')                      
            else:  
                if(not field.verbose_name ==  'ID' and not field.name == 'ownership_other' and not field.name == 'funded_by_other'   and not field.name == "attachments" and not field.name == "focusIndustry"):
                    filters.append(field.verbose_name)
                    context['filters'] = filters
        context['connect'] = Connect.objects.filter(Q(responser=request.user.id) | Q(requester=request.user.id))
        context['iah'] = IncubatorsAccelatorsHub.objects.exclude(Q(profile__user=request.user.id) ).filter(service='Hub')
        context['iah']= getFilteredOf(context['iah'],request,context['connect'])
        if request.user.is_authenticated:
            connectList = Connect.objects.filter(Q(responser=request.user.id)|Q(requester=request.user.id))
            context['connectList']=connectList
            return render(request,'main/iah.html', context)
        else:
            connectList = Connect.objects.exclude(responser=request.user.id,requester=request.user.id)
            context['connect'] = Connect.objects.filter(Q(responser=request.user.id) | Q(requester=request.user.id)).filter(service='Hub')
            context['iah'] = IncubatorsAccelatorsHub.objects.filter(profile__user__is_active=True).exclude(profile__user=request.user.id)
            context['iah']= getFilteredOf(context['iah'],request,context['connect'])
            return render(request,'main/iah.html', context)

    if(typeOf=='acclerator'):
        for field in IncubatorsAccelatorsHub._meta.get_fields(include_parents=False):
            if isinstance(field, models.OneToOneField):
                if field.name=='description':
                        for f in field.related_model._meta.get_fields(include_parents=False):
                            if( str(f.name) ==  'name' or str(f.name)=='sector'):
                                filters.append(f.verbose_name)
                if field.name=='address':
                        for f in field.related_model._meta.get_fields(include_parents=False):
                            if( str(f.name) ==  'location' ):
                                filters.append('Address')                      
            else:  
                if(not field.verbose_name ==  'ID' and not field.name == 'ownership_other' and not field.name == 'funded_by_other'   and not field.name == "attachments" and not field.name == "focusIndustry"):
                    filters.append(field.verbose_name)
                    context['filters'] = filters
        context['connect'] = Connect.objects.filter(Q(responser=request.user.id) | Q(requester=request.user.id))
        context['iah'] = IncubatorsAccelatorsHub.objects.exclude(Q(profile__user=request.user.id) ).filter(service='Accelerator')
        context['iah']= getFilteredOf(context['iah'],request,context['connect'])
        if request.user.is_authenticated:
            connectList = Connect.objects.filter(Q(responser=request.user.id)|Q(requester=request.user.id))
            context['connectList']=connectList
            return render(request,'main/iah.html', context)
        else:
            connectList = Connect.objects.exclude(responser=request.user.id,requester=request.user.id)
            context['connect'] = Connect.objects.filter(Q(responser=request.user.id) | Q(requester=request.user.id))
            context['iah'] = IncubatorsAccelatorsHub.objects.filter(profile__user__is_active=True).exclude(profile__user=request.user.id).filter(service='Accelerator')
            context['iah']= getFilteredOf(context['iah'],request,context['connect'])
            return render(request,'main/iah.html', context)
    
    if(typeOf=='investor'):
        for field in DonorFunder._meta.get_fields(include_parents=False):
            if isinstance(field, models.OneToOneField):
                if field.name=='description':
                        for f in field.related_model._meta.get_fields(include_parents=False):
                            if( str(f.name) ==  'name' or str(f.name)=='sector'):
                                filters.append(f.verbose_name)
                if field.name=='address':
                        for f in field.related_model._meta.get_fields(include_parents=False):
                            if( str(f.name) ==  'location' ):
                                filters.append('Address')                      
            else:  
                if(not field.verbose_name ==  'ID' and not field.name == 'donor_type_by_other' and not field.name == 'investment_type_other' and not  field.name == "max_investment_range"):
                    filters.append(field.verbose_name)
                    context['filters'] = filters
        context['connect'] = Connect.objects.filter(Q(responser=request.user.id) | Q(requester=request.user.id))
        context['investor'] = DonorFunder.objects.exclude(Q(profile__user=request.user.id) )
        context['investor']= getFilteredOf(context['investor'],request,context['connect'])
        if request.user.is_authenticated:
            connectList = Connect.objects.filter(Q(responser=request.user.id)|Q(requester=request.user.id))
            context['connectList']=connectList
            return render(request,'main/investor.html', context)
        else:
            connectList = Connect.objects.exclude(responser=request.user.id,requester=request.user.id)
            context['connect'] = Connect.objects.filter(Q(responser=request.user.id) | Q(requester=request.user.id))
            context['investor'] = DonorFunder.objects.filter(profile__user__is_active=True).exclude(profile__user=request.user.id)
            context['investor']= getFilteredOf(context['investor'],request,context['connect'])
        return render(request,'main/investor.html', context)
    
    if(typeOf=='government'):
        for field in Government._meta.get_fields(include_parents=False):
            if isinstance(field, models.OneToOneField):
                if field.name=='description':
                        for f in field.related_model._meta.get_fields(include_parents=False):
                            if( str(f.name) ==  'name' or str(f.name)=='sector'):
                                filters.append(f.verbose_name)
                if field.name=='address':
                        for f in field.related_model._meta.get_fields(include_parents=False):
                            if( str(f.name) ==  'location' ):
                                filters.append('Address')                      
            else:  
                if(not field.verbose_name ==  'ID' and not field.name == 'GOVERNMENT_TYPE_other' ):
                    filters.append(field.verbose_name)
                    context['filters'] = filters
                    context['connect'] = Connect.objects.filter(Q(responser=request.user.id) | Q(requester=request.user.id))
        context['investor'] = Government.objects.exclude(Q(profile__user=request.user.id) )
        context['investor']= getFilteredOf(context['investor'],request,context['connect'])
        if request.user.is_authenticated:
            connectList = Connect.objects.filter(Q(responser=request.user.id)|Q(requester=request.user.id))
            context['connectList']=connectList
            return render(request,'main/government.html', context)
        else:
            connectList = Connect.objects.exclude(responser=request.user.id,requester=request.user.id)
            investor = Government.objects.filter(profile__user__is_active=True)
            context['investor'] = investor  
        return render(request,'main/government.html', context)
  
    if(typeOf=='doner' ):
        for field in DonorFunder._meta.get_fields(include_parents=False):
            if isinstance(field, models.OneToOneField):
                if field.name=='description':
                        for f in field.related_model._meta.get_fields(include_parents=False):
                            if( str(f.name) ==  'name' or str(f.name)=='sector'):
                                filters.append(f.verbose_name)
                if field.name=='address':
                        for f in field.related_model._meta.get_fields(include_parents=False):
                            if( str(f.name) ==  'location' ):
                                filters.append('Address')                      
            else:  
                if(not field.verbose_name ==  'ID' and not field.name == 'donor_type_by_other' and not field.name == 'investment_type_other' and not  field.name == "max_investment_range"):
                    filters.append(field.verbose_name)
                    context['filters'] = filters
        context['connect'] = Connect.objects.filter(Q(responser=request.user.id) | Q(requester=request.user.id))
        context['investor'] = DonorFunder.objects.exclude(Q(profile__user=request.user.id) )
        context['investor']= getFilteredOf(context['investor'],request,context['connect'])
        if request.user.is_authenticated:
            connectList = Connect.objects.filter(Q(responser=request.user.id)|Q(requester=request.user.id))
            context['connectList']=connectList
            return render(request,'main/investor.html', context)
        else:
            connectList = Connect.objects.exclude(responser=request.user.id,requester=request.user.id)
            context['connect'] = Connect.objects.filter(Q(responser=request.user.id) | Q(requester=request.user.id))
            context['investor'] = DonorFunder.objects.filter(profile__user__is_active=True).exclude(profile__user=request.user.id)
            context['investor']= getFilteredOf(context['investor'],request,context['connect'])
        return render(request,'main/investor.html', context)

    



def register(request):
    context = {}
    if request.method == 'POST':
        context['Government_form'] = GovernmentForm(request.POST, None)
        context['donor_form'] = DonerFunderForm(request.POST, None)
        context['incubator_form'] = IncubatorsAccelatorsHubForm(request.POST, None)
        context['incubator_description'] = DescriptionIncubatorForm(request.POST, request.FILES)
        context['mentor_form'] = MentorForm(request.POST, None)
        context['startup_form'] = StartupForm(request.POST, None)
        context['description'] = DescriptionForm(request.POST, request.FILES)
        context['region_form'] = RegionForm(request.POST, None)
        context['wereda_form'] = WeredaForm(request.POST, None)
        context['address'] = AddressForm(request.POST, None)
        context['user_form'] = UserForm(request.POST, None)
        context['profile'] = ProfileForm(request.POST, request.FILES)

        if request.POST['Startup'] == 'Startup':
            try:
                group = Group.objects.get(name=request.POST['Startup'])
                valid_startup = context['startup_form'].is_valid()
                valid_descriptions = context['description'].is_valid()
                valid_region = context['region_form'].is_valid()
                valid_address = context['address'].is_valid()
                valid_profile = context['profile'].is_valid()
                valid_user = context['user_form'].is_valid()
                address_instance = context['address'].cleaned_data
                description_instance = context['description'].cleaned_data
                profile_instance = context['profile'].cleaned_data
                startup_instance = context['startup_form'].cleaned_data
                user_instance = context['user_form'].cleaned_data

                if valid_descriptions and valid_startup and valid_region and valid_address and valid_profile and valid_user:
                    with transaction.atomic():
                        save_startup(startup_instance, request, description_instance, address_instance, user_instance,
                                    profile_instance, group, context)
                        messages.info(request, "Registration successful please wait till admin approval.")
                    return redirect("main:homepage")
                else:
                    error_messages = []
                    error_messages.append("Validation errors occurred. Please check the form.")
                    for field, errors in context['description'].errors.items():
                        error_messages.append("Error in field {}: {}".format(field, errors))
                    for field, errors in context['region_form'].errors.items():
                        error_messages.append("Error in field {}: {}".format(field, errors))
                    for field, errors in context['address'].errors.items():
                        error_messages.append("Error in field {}: {}".format(field, errors))
                    for field, errors in context['description'].errors.items():
                        error_messages.append("Error in field {}: {}".format(field, errors))
                    for field, errors in context['profile'].errors.items():
                        error_messages.append("Error in field {}: {}".format(field, errors))
                    for field, errors in context['startup_form'].errors.items():
                        error_messages.append("Error in field {}: {}".format(field, errors))
                    for field, errors in context['user_form'].errors.items():
                        error_messages.append("Error in field {}: {}".format(field, errors))
                        

                    messages.error(request, "<br>".join(error_messages))
                    return redirect("main:register")

            except Group.DoesNotExist:
                messages.error(request, "The specified group does not exist.")
                return redirect("main:register")
            except DatabaseError as e:
                messages.error(request, "Database Error: {}".format(e))
                return redirect("main:register")
            except Exception as e:
                messages.error(request, "Unexpected Error: {}".format(e))
                return redirect("main:register")

 

        if request.POST['Startup'] == 'Mentor':
            try:
                group = Group.objects.get(name=request.POST['Startup'])
                valid_mentor = context['mentor_form'].is_valid()
                valid_descriptions = context['description'].is_valid()
                valid_region = context['region_form'].is_valid()
                valid_address = context['address'].is_valid()
                valid_profile = context['profile'].is_valid()
                valid_user = context['user_form'].is_valid()
                address_instance = context['address'].cleaned_data
                description_instance = context['description'].cleaned_data
                profile_instance = context['profile'].cleaned_data
                mentor_instance = context['mentor_form'].cleaned_data
                user_instance = context['user_form'].cleaned_data

                if valid_descriptions and valid_mentor and valid_region and valid_address and valid_profile and valid_user:
                    with transaction.atomic():
                        save_mentor(mentor_instance, request, description_instance, address_instance, user_instance,
                                    profile_instance, group, context)
                        messages.info(request, "Registration successful please wait till admin approval.")
                    return redirect("main:homepage")
                else:
                    error_messages = []
                    error_messages.append("Validation errors occurred. Please check the form.")
                    for field, errors in context['description'].errors.items():
                        error_messages.append("Error in field {}: {}".format(field, errors))
                    for field, errors in context['region_form'].errors.items():
                        error_messages.append("Error in field {}: {}".format(field, errors))
                    for field, errors in context['address'].errors.items():
                        error_messages.append("Error in field {}: {}".format(field, errors))
                    for field, errors in context['description'].errors.items():
                        error_messages.append("Error in field {}: {}".format(field, errors))
                    for field, errors in context['profile'].errors.items():
                        error_messages.append("Error in field {}: {}".format(field, errors))
                    for field, errors in context['mentor_form'].errors.items():
                        error_messages.append("Error in field {}: {}".format(field, errors))
                    for field, errors in context['user_form'].errors.items():
                        error_messages.append("Error in field {}: {}".format(field, errors))

                    messages.error(request, "<br>".join(error_messages))
                    return redirect("main:register")

            except Group.DoesNotExist:
                messages.error(request, "The specified group does not exist.")
                return redirect("main:register")
            except DatabaseError as e:
                messages.error(request, "Database Error: {}".format(e))
                return redirect("main:register")
            except Exception as e:
                messages.error(request, "Unexpected Error: {}".format(e))
                return redirect("main:register")

        if request.POST['Startup'] == 'Incubator/Hub/Accelerator':
            try:
                group = Group.objects.get(name=request.POST['Startup'])
                valid_incubator_description = context['incubator_description'].is_valid()
                valid_incubator = context['incubator_form'].is_valid()
                valid_region = context['region_form'].is_valid()
                valid_address = context['address'].is_valid()
                valid_profile = context['profile'].is_valid()
                valid_user = context['user_form'].is_valid()
                address_instance = context['address'].cleaned_data
                incubator_description_instance = context['incubator_description'].cleaned_data
                profile_instance = context['profile'].cleaned_data
                incubator_instance = context['incubator_form'].cleaned_data
                user_instance = context['user_form'].cleaned_data

                if valid_incubator_description and valid_incubator and valid_region and valid_address and valid_profile and valid_user:
                    with transaction.atomic():
                        save_incubator(incubator_instance, request, incubator_description_instance, address_instance,
                                    user_instance, profile_instance, group, context)
                        messages.info(request, "Registration successful please wait till admin approval.")
                    return redirect("main:homepage")
                else:
                    error_messages = []
                    error_messages.append("Validation errors occurred. Please check the form.")
                    for field, errors in context['incubator_description'].errors.items():
                        error_messages.append("Error in field {}: {}".format(field, errors))
                    for field, errors in context['incubator_form'].errors.items():
                        error_messages.append("Error in field {}: {}".format(field, errors))
                    for field, errors in context['region_form'].errors.items():
                        error_messages.append("Error in field {}: {}".format(field, errors))
                    for field, errors in context['address'].errors.items():
                        error_messages.append("Error in field {}: {}".format(field, errors))
                    for field, errors in context['profile'].errors.items():
                        error_messages.append("Error in field {}: {}".format(field, errors))
                    for field, errors in context['user_form'].errors.items():
                        error_messages.append("Error in field {}: {}".format(field, errors))

                    messages.error(request, "<br>".join(error_messages))
                    return redirect("main:register")

            except Group.DoesNotExist:
                messages.error(request, "The specified group does not exist.")
                return redirect("main:register")
            except DatabaseError as e:
                messages.error(request, "Database Error: {}".format(e))
                return redirect("main:register")
            except Exception as e:
                messages.error(request, "Unexpected Error: {}".format(e))
                return redirect("main:register")

        if request.POST['Startup'] == 'Funder/Donor':
            try:
                group = Group.objects.get(name=request.POST['Startup'])
                valid_donor = context['donor_form'].is_valid()
                valid_descriptions = context['description'].is_valid()
                valid_region = context['region_form'].is_valid()
                valid_address = context['address'].is_valid()
                valid_profile = context['profile'].is_valid()
                valid_user = context['user_form'].is_valid()
                address_instance = context['address'].cleaned_data
                description_instance = context['description'].cleaned_data
                profile_instance = context['profile'].cleaned_data
                donor_instance = context['donor_form'].cleaned_data
                user_instance = context['user_form'].cleaned_data

                if valid_descriptions and valid_donor and valid_region and valid_address and valid_profile and valid_user:
                    with transaction.atomic():
                        save_donor(donor_instance, request, description_instance, address_instance, user_instance,
                                profile_instance, group, context)
                        messages.info(request, "Registration successful please wait till admin approval.")
                    return redirect("main:homepage")
                else:
                    error_messages = []
                    error_messages.append("Validation errors occurred. Please check the form.")
                    for field, errors in context['donor_form'].errors.items():
                        error_messages.append("Error in field {}: {}".format(field, errors))
                    for field, errors in context['description'].errors.items():
                        error_messages.append("Error in field {}: {}".format(field, errors))
                    for field, errors in context['region_form'].errors.items():
                        error_messages.append("Error in field {}: {}".format(field, errors))
                    for field, errors in context['address'].errors.items():
                        error_messages.append("Error in field {}: {}".format(field, errors))
                    for field, errors in context['profile'].errors.items():
                        error_messages.append("Error in field {}: {}".format(field, errors))
                    for field, errors in context['user_form'].errors.items():
                        error_messages.append("Error in field {}: {}".format(field, errors))

                    messages.error(request, "<br>".join(error_messages))
                    return redirect("main:register")

            except Group.DoesNotExist:
                messages.error(request, "The specified group does not exist.")
                return redirect("main:register")
            except DatabaseError as e:
                messages.error(request, "Database Error: {}".format(e))
                return redirect("main:register")
            except Exception as e:
                messages.error(request, "Unexpected Error: {}".format(e))
                return redirect("main:register")

        if request.POST['Startup'] == 'Government':
            try:
                group = Group.objects.get(name=request.POST['Startup'])
                valid_government = context['Government_form'].is_valid()
                valid_descriptions = context['description'].is_valid()
                valid_region = context['region_form'].is_valid()
                valid_address = context['address'].is_valid()
                valid_profile = context['profile'].is_valid()
                valid_user = context['user_form'].is_valid()
                address_instance = context['address'].cleaned_data
                description_instance = context['description'].cleaned_data
                profile_instance = context['profile'].cleaned_data
                government_instance = context['Government_form'].cleaned_data
                user_instance = context['user_form'].cleaned_data

                if valid_descriptions and valid_government and valid_region and valid_address and valid_profile and valid_user:
                    with transaction.atomic():
                        save_government(government_instance, request, description_instance, address_instance, user_instance,
                                        profile_instance, group, context)
                        messages.info(request, "Registration successful please wait till admin approval.")
                    return redirect("main:homepage")
                else:
                    error_messages = []
                    error_messages.append("Validation errors occurred. Please check the form.")
                    for field, errors in context['Government_form'].errors.items():
                        error_messages.append("Error in field {}: {}".format(field, errors))
                    for field, errors in context['description'].errors.items():
                        error_messages.append("Error in field {}: {}".format(field, errors))
                    for field, errors in context['region_form'].errors.items():
                        error_messages.append("Error in field {}: {}".format(field, errors))
                    for field, errors in context['address'].errors.items():
                        error_messages.append("Error in field {}: {}".format(field, errors))
                    for field, errors in context['profile'].errors.items():
                        error_messages.append("Error in field {}: {}".format(field, errors))
                    for field, errors in context['user_form'].errors.items():
                        error_messages.append("Error in field {}: {}".format(field, errors))
                    print(error_messages)
                    messages.error(request, "<br>".join(error_messages))
                    return redirect("main:register")

            except Group.DoesNotExist:
                messages.error(request, "The specified group does not exist.")
                return redirect("main:register")
            except DatabaseError as e:
                messages.error(request, "Database Error: {}".format(e))
                return redirect("main:register")
            except Exception as e:
                messages.error(request, "Unexpected Error: {}".format(e))
                return redirect("main:register")

        # return redirect("main:homepage")
    else:
        context['mentor_form'] = MentorForm()
        context['incubator_form'] = IncubatorsAccelatorsHubForm()
        context['donor_form'] = DonerFunderForm()
        context['Government_form'] = GovernmentForm()
        context['startup_form'] = StartupForm()
        context['description'] = DescriptionForm()
        context['address'] = AddressForm()
        context['profile'] = ProfileForm()
        context['region_form'] = RegionForm()
        context['wereda_form'] = WeredaForm()
        context['user_form'] = UserForm()
        return render(request, 'main/registration.html', context)
    

def filter(request,typeOf):
    if request.method== 'POST':
        if typeOf=='startup':
            filterParams=json.loads(list(request.POST)[0])
            
            if filterParams:
                startup = Startup.objects.all()
                for param in filterParams:
                    if param=='market_scope':
                        if filterParams[param]:
                            startup = startup.filter(market_scope__in = filterParams[param])     
                    if param=='stage':
                        if filterParams[param]:
                            startup = startup.filter(stage__in = filterParams[param]) 
                    if param=='daterange':
                        if filterParams[param]:
                            startup =  startup.filter(establishment_year__gte=filterParams[param].split(' - ')[0],
                                        establishment_year__lte=filterParams[param].split(' - ')[1])  
                    if param=='name':
                        if filterParams[param]:
                            q_objects = [Q(description__name__startswith=str(item)) for item in filterParams[param]]
                            query = reduce(or_, q_objects)
                            startup = startup.filter(query)      
                    if param == 'sector':
                        if filterParams[param]:
                            q_objects = [Q(description__sector__startswith=str(item)) for item in filterParams[param]]
                            query = reduce(or_, q_objects)
                            startup = startup.filter(query)
                    if param == 'regionn':
                        if filterParams[param]:
                            startup = startup.filter(address__location__region__region_name=filterParams[param])
                    if param == 'wereda':
                        if filterParams[param]:
                            startup = startup.filter(address__location__wereda_name=filterParams[param])
                context['startups'] = startup.filter(profile__user__is_active=True)
                return render(request,'main/startup_filters.html',context)
        if typeOf=='mentor':
            filterParams=json.loads(list(request.POST)[0])
            if filterParams:
                mentor = Mentor.objects.all()
                for param in filterParams:
                    if param=='educational_level':
                        if filterParams[param]:
                            mentor = mentor.filter(educational_level__in = filterParams[param])     
                    if param=='educational_background':
                        if filterParams[param]:
                            mentor = mentor.filter(educational_background__in = filterParams[param]) 
                    if param=='name':
                        if filterParams[param]:
                            q_objects = [Q(description__name__startswith=str(item)) for item in filterParams[param]]
                            query = reduce(or_, q_objects)
                            mentor = mentor.filter(query)      
                    if param == 'sector':
                        if filterParams[param]:
                            q_objects = [Q(description__sector__startswith=str(item)) for item in filterParams[param]]
                            query = reduce(or_, q_objects)
                            mentor = mentor.filter(query)   
                             
                    if param == 'mentor_area':
                        if filterParams[param]:
                            q_objects = [Q(mentor_area__startswith=str(item)) for item in filterParams[param]]
                            query = reduce(or_, q_objects)
                            mentor = mentor.filter(query)     
                    
                    if param=='airelated_expriance':
                        if filterParams[param]:
                            # query = reduce(or_, (Q(description__sector__startswith=item) for item in filterParams[param]))
                            mentor = mentor.filter(airelated_expriance=not None) 
                    if param == 'regionn':
                        if filterParams[param]:
                            mentor = mentor.filter(address__location__regionId__region_name=filterParams[param])
                    if param == 'wereda':
                        if filterParams[param]:
                            mentor = mentor.filter(address__location__wereda_name=filterParams[param])
                context['mentors'] = mentor
                return render(request,'main/mentor_filters.html',context)
            
        if typeOf=='iah':
            filterParams=json.loads(list(request.POST)[0])
            if filterParams:
                iah = IncubatorsAccelatorsHub.objects.all()
                for param in filterParams:
                    if param=='service':
                        if filterParams[param]:
                            iah = iah.filter(service__in=filterParams[param])
                    if param=='ownership':
                        if filterParams[param]:
                            iah = iah.filter(ownership__in=filterParams[param]) 
                    if param=='level':
                        if filterParams[param]:
                            query = reduce(or_, (Q(level__in=item) for item in filterParams[param]))
                            iah = iah.filter(query)
                    if param=='name':
                        if filterParams[param]:
                            query = reduce(or_, (Q(description__name__startswith=item) for item in filterParams[param]))
                            iah = iah.filter(query)       
                    if param=='sector':
                        if filterParams[param]:
                            query = reduce(or_, (Q(description__sector__startswith=item) for item in filterParams[param]))
                            iah = iah.filter(query) 
                    if param=='funded_by':
                        if filterParams[param]:
                            iah = iah.filter(funded_by__in=filterParams[param]) 
                    if param=='program_duration':
                        if filterParams[param]:
                            query = reduce(or_, (Q(program_duration__in=item) for item in filterParams[param]))
                            iah = iah.filter(query) 
                    if param == 'regionn':
                        if filterParams[param]:
                            iah = iah.filter(address__location__region__region_name=filterParams[param])
                    if param == 'wereda':
                        if filterParams[param]:
                            iah = iah.filter(address__location__wereda_name=filterParams[param])
                context['iahs'] = iah
                return render(request,'main/iah_filters.html',context)   
        return render(request,'main/iah_filters.html',context)
             


def networksFromfunc(request,typeOf):
    filters=[]
    if(typeOf=='startup'):
        for field in Startup._meta.get_fields(include_parents=False):
            if isinstance(field, models.OneToOneField):
                if field.name=='description':
                        for f in field.related_model._meta.get_fields(include_parents=False):
                            if( str(f.name) ==  'name' or str(f.name)=='sector'):
                                filters.append(f.verbose_name)
                if field.name=='address':
                        for f in field.related_model._meta.get_fields(include_parents=False):
                            if( str(f.name) ==  'location' ):
                                filters.append('Address')
                                        
            else:  
                if(not field.verbose_name ==  'ID'):
                    filters.append(field.verbose_name)
                    context['filters'] = filters    
        context['connect'] = Connect.objects.filter(Q(responser=request.user.id) | Q(requester=request.user.id))
        context['startups'] = Startup.objects.exclude(profile__user=request.user.id)
        context['startups']= getFilteredOf(context['startups'],request,context['connect'])

        if request.user.is_authenticated:
            connectList = Connect.objects.filter(Q(responser=request.user.id)|Q(requester=request.user.id))
            context['connectList']=connectList
            context['fromFunc']=True
            return render(request,'main/startup.html', context)
        else:
            connectList = Connect.objects.exclude(responser=request.user.id,requester=request.user.id)
            context['connect'] = Connect.objects.filter(Q(responser=request.user.id) | Q(requester=request.user.id))
            context['startups'] = Startup.objects.exclude(profile__user=request.user.id)
            context['startups']= getFilteredOf(context['startups'],request,context['connect'])
            context['fromFunc']=True
            return render(request,'main/startup.html', context)
    if(typeOf=='mentor'):
        for field in Mentor._meta.get_fields(include_parents=False):
            if isinstance(field, models.OneToOneField):
                if field.name=='description':
                        for f in field.related_model._meta.get_fields(include_parents=False):
                            if( str(f.name) ==  'name' or str(f.name)=='sector'):
                                filters.append(f.verbose_name)
                if field.name=='address':
                        for f in field.related_model._meta.get_fields(include_parents=False):
                            if( str(f.name) ==  'location' ):
                                filters.append('Address')                      
            else:  
                if(not field.verbose_name ==  'ID' and not field.name == 'educational_level_other' and not field.name == 'educational_background_other' and not field.name == "mentor_area_other" and not field.name == "attachments"):
                    filters.append(field.verbose_name)
                    context['filters'] = filters  
        if request.user.is_authenticated:
            mentors = Mentor.objects.filter(profile__user__is_active=True).exclude(profile__user=request.user.id)
            context['mentors'] = mentors
            connectList = Connect.objects.filter(Q(responser=request.user.id)|Q(requester=request.user.id))
            context['connectList']=connectList
            context['fromFunc']=True
            return render(request,'main/mentor.html', context)
        else:
            connectList = Connect.objects.exclude(responser=request.user.id,requester=request.user.id)
            mentors = Mentor.objects.filter(profile__user__is_active=True)
            context['mentors'] = mentors
            context['fromFunc']=True
        return render(request,'main/mentor.html', context)
    if(typeOf=='incubator'):
        for field in IncubatorsAccelatorsHub._meta.get_fields(include_parents=False):
            if isinstance(field, models.OneToOneField):
                if field.name=='description':
                        for f in field.related_model._meta.get_fields(include_parents=False):
                            if( str(f.name) ==  'name' or str(f.name)=='sector'):
                                filters.append(f.verbose_name)
                if field.name=='address':
                        for f in field.related_model._meta.get_fields(include_parents=False):
                            if( str(f.name) ==  'location' ):
                                filters.append('Address')                      
            else:  
                if(not field.verbose_name ==  'ID' and not field.name == 'ownership_other' and not field.name == 'funded_by_other'   and not field.name == "attachments" and not field.name == "focusIndustry"):
                    filters.append(field.verbose_name)
                    context['filters'] = filters
        if request.user.is_authenticated:
            iah = IncubatorsAccelatorsHub.objects.filter(profile__user__is_active=True).exclude(profile__user=request.user.id)
            context['iah'] = iah
            connectList = Connect.objects.filter(Q(responser=request.user.id)|Q(requester=request.user.id))
            context['connectList']=connectList
            context['fromFunc']=True
            return render(request,'main/iah.html', context)
        else:
            connectList = Connect.objects.exclude(responser=request.user.id,requester=request.user.id)
            iah = IncubatorsAccelatorsHub.objects.filter(profile__user__is_active=True)
            context['iah'] = iah  
            context['fromFunc']=True
        return render(request,'main/iah.html', context)
    if(typeOf=='investor'):
        for field in DonorFunder._meta.get_fields(include_parents=False):
            if isinstance(field, models.OneToOneField):
                if field.name=='description':
                        for f in field.related_model._meta.get_fields(include_parents=False):
                            if( str(f.name) ==  'name' or str(f.name)=='sector'):
                                filters.append(f.verbose_name)
                if field.name=='address':
                        for f in field.related_model._meta.get_fields(include_parents=False):
                            if( str(f.name) ==  'location' ):
                                filters.append('Address')                      
            else:  
                if(not field.verbose_name ==  'ID' and not field.name == 'donor_type_by_other' and not field.name == 'investment_type_other' and not  field.name == "max_investment_range"):
                    filters.append(field.verbose_name)
                    context['filters'] = filters
        if request.user.is_authenticated:
            investor = DonorFunder.objects.filter(profile__user__is_active=True).exclude(profile__user=request.user.id)
            context['investor'] = investor
            connectList = Connect.objects.filter(Q(responser=request.user.id)|Q(requester=request.user.id))
            context['connectList']=connectList
            context['fromFunc']=True
            return render(request,'main/investor.html', context)
        else:
            connectList = Connect.objects.exclude(responser=request.user.id,requester=request.user.id)
            investor = DonorFunder.objects.filter(profile__user__is_active=True)
            context['investor'] = investor  
            context['fromFunc']=True 
        return render(request,'main/investor.html', context)
    
    if(typeOf=='government'):
        for field in Government._meta.get_fields(include_parents=False):
            if isinstance(field, models.OneToOneField):
                if field.name=='description':
                        for f in field.related_model._meta.get_fields(include_parents=False):
                            if( str(f.name) ==  'name' or str(f.name)=='sector'):
                                filters.append(f.verbose_name)
                if field.name=='address':
                        for f in field.related_model._meta.get_fields(include_parents=False):
                            if( str(f.name) ==  'location' ):
                                filters.append('Address')                      
            else:  
                if(not field.verbose_name ==  'ID' and not field.name == 'GOVERNMENT_TYPE_other' ):
                    filters.append(field.verbose_name)
                    context['filters'] = filters
        if request.user.is_authenticated:
            investor = DonorFunder.objects.filter(profile__user__is_active=True).exclude(profile__user=request.user.id)
            context['investor'] = investor
            connectList = Connect.objects.filter(Q(responser=request.user.id)|Q(requester=request.user.id))
            context['connectList']=connectList
            context['fromFunc']=True 
            return render(request,'main/government.html', context)
        else:
            connectList = Connect.objects.exclude(responser=request.user.id,requester=request.user.id)
            investor = DonorFunder.objects.filter(profile__user__is_active=True)
            context['investor'] = investor  
        return render(request,'main/government.html', context)





@csrf_exempt
def getContent(request,typeOf):
    return networksFromfunc(request,typeOf)
    # if typeOf == 'startups':
    #       context['startups'] = Startup.objects.filter(profile__user__is_active=True).exclude(profile__user=request.user.id) if request.user.is_authenticated else Startup.objects.filter(profile__user__is_active=True)
    #       return  render(request,'main/startup_content.html',context)
    # if typeOf == 'mentors':
    #       print(typeOf)
    # if typeOf == 'incubators':
    #       print(typeOf)
    # if typeOf == 'hubs':
    #       print(typeOf)
    # if typeOf == 'acclerators':
    #       print(typeOf)
    # if typeOf == 'doners':
    #       print(typeOf)
    # if typeOf == 'funder':
    #       print(typeOf)
    # if typeOf == 'government':
    #       print(typeOf)
    
     
    # return render(request,'main/startup_filters.html',context)
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('main:login'))






from django.shortcuts import render, redirect
from django.views import View
from .models import Message  # Import your Message model
from django.contrib.auth.models import User  # Import the User model

class ComposeMessageView(View):
    template_name = 'messages/compose_message.html'

    def get(self, request):
        users = User.objects.all()
        return render(request, self.template_name, {'users': users})

    def post(self, request):
        sender = request.user
        recipients = request.POST.getlist('recipients')
        message_text = request.POST.get('message_text')

        if recipients and message_text:
            message = Message(sender=sender, recipients=recipients, message=message_text)
            message.save()
            return redirect('inbox')  # Redirect to the inbox page or wherever you want to go after sending the message

        # Handle form errors if recipients or message_text is empty
        users = User.objects.all()
        return render(request, self.template_name, {'users': users, 'error_message': 'Please select recipients and enter a message.'})
