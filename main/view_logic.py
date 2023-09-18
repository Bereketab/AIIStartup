from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from .models import *
from .forms import *
from django.contrib.auth.models import User,Group
from django.db import DatabaseError, transaction
from .models import *
from django.shortcuts import render,redirect
from .forms import *
from django.contrib import messages

def save_wereda(context):
    region = EthRegion.objects.get(region_name=context['region_form'].cleaned_data['region_name'])
    wereda = Wereda(wereda_name=context['wereda_form'].data['wereda_name'], region=region)
    wereda.save()
    return wereda


def save_description(request, description_instance):
    def check_sector():
        if description_instance['sector'] == 'Other':
            return request.POST['other__sector']
        else:
            return ''

    description = Description(
        name=description_instance['name'],
        description=description_instance['description'],
        sector=description_instance['sector'],
        logo=description_instance['logo'],
        other_sector=check_sector(),
    )
    description.save()
    return description


def save_incubator_description(request, incubator_description_instance):
    description = Description(
        name=incubator_description_instance['name'],
        description=incubator_description_instance['description'],
        sector='Other',
        logo=incubator_description_instance['logo'],
        other_sector='no',
    )
    description.save()
    return description


def save_address(request, address_instance, context):
    address = Address(
        country='Ethiopia',
        location=save_wereda(context),
        phone_number=address_instance['phone_number'],
        city_name=address_instance['city_name'],
        website=address_instance['website'],
    )
    address.save()
    return address


def save_user(user_instance):
    usero = User(
        username=user_instance['username'],
        email=user_instance['email'],
        is_active=False,
        first_name=user_instance['first_name'],
        last_name=user_instance['last_name']
    )
    usero.set_password(user_instance['password'])
    usero.save()
    return usero


def save_profile(user_instance, profile_instance, group):
    profile = Profile(
        middle_name=profile_instance['middle_name'],
        birth_date=profile_instance['birth_date'],
        user=save_user(user_instance),
        profile_pic=profile_instance['profile_pic'],
        contact=profile_instance['contact'],
        secondary_email=profile_instance['secondary_email'],
        gender=profile_instance['gender'],
        group=group
    )
    profile.save()
    return profile


def save_donor(donor_instance, request, description_instance, address_instance, user_instance, profile_instance, group, context):
    def check_donor():
        if donor_instance['donor_type'] == 'Other':
            return request.POST['other__donor_type']
        else:
            return ''

    def check_investment():
        if donor_instance['investment_type'] == 'Other':
            return request.POST['other__investment_type']
        else:
            return ''

    donor = DonorFunder(
        donor_type=donor_instance['donor_type'],
        donor_type_by_other=check_donor(),
        level=donor_instance['level'],
        investment_type=donor_instance['investment_type'],
        investment_type_other=check_investment(),
        max_investment_range=donor_instance['max_investment_range'],
        description=save_description(request, description_instance),
        address=save_address(request, address_instance, context),
        profile=save_profile(user_instance, profile_instance, group)
    )
    donor.save()
    return donor


def save_startup(startup_instance, request, description_instance, address_instance, user_instance, profile_instance, group, context):
    startup = Startup(
        establishment_year=startup_instance['establishment_year'],
        market_scope=startup_instance['market_scope'],
        stage=startup_instance['stage'],
        description=save_description(request, description_instance),
        address=save_address(request, address_instance, context),
        profile=save_profile(user_instance, profile_instance, group)
    )
    startup.save()
    return startup


def save_government(government_instance, request, description_instance, address_instance, user_instance, profile_instance, group, context):
    def check_investment():
        if government_instance['GOVERNMENT_TYPE'] == 'Other':
            return request.POST['other__Government_type']
        else:
            return ''

    government = Government(
        GOVERNMENT_TYPE=government_instance['GOVERNMENT_TYPE'],
        GOVERNMENT_TYPE_other=check_investment(),
        level=government_instance['level'],
        description=save_description(request, description_instance),
        address=save_address(request, address_instance, context),
        profile=save_profile(user_instance, profile_instance, group)
    )
    government.save()
    return government


def save_incubator(incubator_instance, request, incubator_description_instance, address_instance, user_instance, profile_instance, group, context):
    def set_funded_other():
        if incubator_instance['funded_by'] == 'Other':
            return request.POST['other__funded_by']
        else:
            return ''

    def set_owner_other():
        if incubator_instance['ownership'] == 'Other':
            return request.POST['other__ownership']
        else:
            return ''

    incubator = IncubatorsAccelatorsHub(
        service=incubator_instance['service'],
        ownership=incubator_instance['ownership'],
        ownership_other=set_owner_other(),
        focusIndustry=incubator_instance['focusIndustry'],
        level=incubator_instance['level'],
        funded_by=incubator_instance['funded_by'],
        funded_by_other=set_funded_other(),
        program_duration=incubator_instance['program_duration'],
        attachments=incubator_instance['attachments'],
        description=save_incubator_description(request, incubator_description_instance),
        address=save_address(request, address_instance, context),
        profile=save_profile(user_instance, profile_instance, group)
    )
    incubator.save()
    return incubator


def save_mentor(mentor_instance, request, description_instance, address_instance, user_instance, profile_instance, group, context):
    print(mentor_instance)
    def check_edu_level():
        if mentor_instance['educational_level'] == 'other':
            return request.POST['other_educational_level']
        else:
            return ''

    def check_background():
        if mentor_instance['educational_background'] == 'other':
            return request.POST['other_educational_background']
        else:
            return ''

    def check_mentor_area():
        if mentor_instance['mentor_area'] == 'other':
            return request.POST['other_mentor_area']
        else:
            return ''

    mentor = Mentor(
        educational_level=mentor_instance['educational_level'],
        educational_level_other=check_edu_level(),
        educational_background=mentor_instance['educational_background'],
        educational_background_other=check_background(),
        mentor_area=mentor_instance['mentor_area'],
        mentor_area_other=check_mentor_area(),
        airelated_expriance=mentor_instance['airelated_expriance'],

        attachments=mentor_instance['attachments'],
        description=save_description(request, description_instance),
        address=save_address(request, address_instance, context),
        profile=save_profile(user_instance, profile_instance, group)
    )
    mentor.save()
    return mentor




def save_government_object(request, context):
    valid_government = context['government_form'].is_valid()
    valid_descriptions = context['description'].is_valid()
    valid_region = context['region_form'].is_valid()
    valid_address = context['address'].is_valid()
    valid_profile = context['profile'].is_valid()
    valid_user = context['user_form'].is_valid()
    print(valid_descriptions)
    if valid_descriptions and valid_government and valid_region and valid_address and valid_profile and valid_user:
        print(request.POST['Startup'])
        group = Group.objects.get(name=request.POST['Startup'])
        address_instance = context['address'].cleaned_data
        description_instance = context['description'].cleaned_data
        profile_instance = context['profile'].cleaned_data
        government_instance = context['government_form'].cleaned_data
        user_instance = context['user_form'].cleaned_data
        try:
            with transaction.atomic():
                save_government(government_instance, request, description_instance, address_instance, user_instance,
                                profile_instance, group, context)
        except DatabaseError as e:
            print(e)
        return redirect("main:homepage")
    else:
        for field, errors in context['government_form'].errors.items():
            print("Error in field {}: {}".format(field, errors))
