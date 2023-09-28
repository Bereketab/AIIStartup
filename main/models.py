from django.contrib.auth.models import User,Group
from .model_variables import *
from django.contrib.postgres.fields import ArrayField
from django.db import models
from .utils import *
from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver




class EthRegion(models.Model):
    region_name = models.CharField(
        verbose_name='Region',
        max_length=50,
        choices=REGIONS_CHOICES,  
        blank=False,
        null=False,
        unique=True
    )

    def __str__(self):
        return self.region_name


class Wereda(models.Model):
    region = models.ForeignKey(EthRegion, on_delete=models.CASCADE, verbose_name='Region', related_name='woredas')  # 3. ForeignKey Defaults
    wereda_name = models.CharField(
        max_length=50,
        verbose_name='Wereda',
        blank=False,
        null=False
    )

    def __str__(self):
        return self.wereda_name


class Address(models.Model):
    country = models.CharField(
        verbose_name='Country',
        max_length=50,
        null=False,
        blank=False
    )
    location = models.OneToOneField(Wereda, on_delete=models.DO_NOTHING, verbose_name='Wereda', null=False, blank=False)
    phone_number = models.IntegerField(
        verbose_name='Phone Number',
        null=False,
        blank=False
    )
    city_name = models.CharField(
        verbose_name='City Name',
        max_length=50,
        blank=False,
        null=False
    )
    website = models.CharField(
        verbose_name='Website',
        max_length=50,
        null=False,
        blank=False
    )

    def __str__(self):
        return self.location.wereda_name


class Description(models.Model):
    name = models.CharField(verbose_name = 'Name',max_length=50,blank=False,null=False)
    description = models.TextField(verbose_name = 'Description',max_length=1000,blank=False,null=False)
    sector = models.CharField(
        verbose_name = 'Sector',
        max_length=50,
        choices=SECTORS,
        blank=False,
        null=False,
        )
    other_sector = models.CharField(
        
        max_length=50,
        blank=True,null=True
    )
    logo = models.ImageField(upload_to='logo/startup',blank=True,null=True)
    def __str__(self):
        return self.name



class Profile(models.Model):
    GENDER = ((0,'Male'),(1,'Female'))
    middle_name = models.CharField(
        verbose_name='Middle Name',
        max_length=50,
        null=False,
        blank=False
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birth_date = models.DateField(verbose_name='Birth Date', null=False, blank=False)
    profile_pic = models.ImageField(
        verbose_name='Profile Picture',
        upload_to='user_pic/%Y/%m/%d',
        blank=False,
        null=False,
        validators=[validate_image]
    )
    contact = models.CharField(verbose_name='Contact', max_length=50, null=False, blank=False)
    secondary_email = models.EmailField(verbose_name='Alternate Email', max_length=150, null=False, blank=False)
    gender = models.IntegerField(verbose_name='Sex/Gender', default=0, choices=GENDER_CHOICES)  # 2. CharField Choices
    friends = models.ManyToManyField('self', blank=True, symmetrical=False)  # 5. Profile Friends
    modified = models.DateTimeField(auto_now=True)
    group = models.ForeignKey(Group, on_delete=models.DO_NOTHING, blank=True, null=True)

    def __str__(self):
        return str(self.user.email)

    def get_absolute_url(self):
        return "/users/{}".format(self.user.id)

class Startup(models.Model):
    establishment_year = models.DateField(verbose_name="Establishment Year", blank=False,null=False)
    market_scope = models.CharField(
        verbose_name = 'Market Scope',
        max_length=50,
        choices=MARKET_SCOPE,
        blank=False,
        null=False,
        )
    stage = models.CharField(
        verbose_name = 'Stage',
        max_length=50,
        choices=STAGE,
        blank=False,
        null=False
        )
    description = models.OneToOneField(Description, on_delete=models.DO_NOTHING,blank=False,null=False,related_name='startup_description')
    address = models.OneToOneField(Address, on_delete=models.DO_NOTHING,blank=False,null=False,related_name='startup_address')
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE,blank=False,null=False,related_name='startup_profile')
    def get_my_model_name(self):
        return self._meta.model_name
    @property
    def is_pending(self):
        return self
    def __str__(self):
        return self.description.name.__str__()
    def get_absolute_url(self):
    	return "/startup/{}".format(self.description.name)

class Mentor(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE,blank=False,null=False,)
    address = models.OneToOneField(Address, on_delete=models.DO_NOTHING,blank=False,null=False,related_name='mentor_address')
    educational_level = models.CharField(
        verbose_name = 'Educational Level',
        choices=EDUCATIONAL_LEVEL,
        max_length=50,blank=False,null=False)
    educational_level_other = models.CharField(
        verbose_name = 'Specify Other Level',
        max_length=50,blank=True,null=True)
    educational_background = models.CharField(
        verbose_name = 'Educational Background',
        choices=EDUCATIONAL_BACKGROUND,
        max_length=50,blank=False,null=False)
    educational_background_other = models.CharField(
        verbose_name = 'Specify Other Background',
        max_length=50,blank=True,null=True)
    mentor_area = models.CharField(
        verbose_name = 'Mentor Area',
        choices=MENTORSHIP_AREA,
        max_length=50,blank=False,null=False)
    mentor_area_other = models.CharField(
        verbose_name = 'Specify Other Area',
        max_length=50,blank=True,null=True)
    airelated_expriance = models.CharField(
        verbose_name = 'AI Related Experience',
        max_length=50,blank=True,null=True)
    attachments = models.FileField(
        verbose_name = 'Attachment',
        upload_to='mentor/attachments',blank=True,null=True, help_text="please upload relevant documents max 10"
        )
    description = models.OneToOneField(Description, on_delete=models.DO_NOTHING,blank=False,null=False,related_name='mentor_description')
    @property
    def is_pending(self):
        return self.middle_name
    def __str__(self):
        return self.description.name.__str__()
    def get_my_model_name(self):
        return self._meta.model_name


class DonorFunder(models.Model):
    donor_type = models.CharField(
        verbose_name='Donor Type',
        max_length=50,
        choices=FUNDED_BY_CHOICES,  
        blank=False,
        null=False
    )
    donor_type_by_other = models.CharField(max_length=50, blank=True, null=True)
    address = models.OneToOneField(Address, on_delete=models.DO_NOTHING, blank=False, null=False, related_name='donor_address')
    level = ArrayField(models.CharField(
        max_length=500,
    ), size=20, default=list, verbose_name='Level')
    investment_type = models.CharField(
        verbose_name='Investment Type',
        max_length=50,
        choices=INVESTMENT_TYPE_CHOICES, 
        blank=False,
        null=False
    )
    investment_type_other = models.CharField(max_length=50, blank=True, null=True)
    profile = models.OneToOneField(Profile, on_delete=models.DO_NOTHING, blank=False, null=False, related_name='donor_profile')
    description = models.OneToOneField(Description, on_delete=models.DO_NOTHING, blank=False, null=False,
                                       related_name='donor_description')
    max_investment_range = models.CharField(verbose_name='Investment Range', max_length=100, blank=True, null=True)

    @property
    def is_pending(self):
        return self

    def __str__(self):
        return self.description.name.__str__()

    def get_my_model_name(self):
        return self._meta.model_name


class IncubatorsAccelatorsHub(models.Model):
    address = models.OneToOneField(Address, on_delete=models.DO_NOTHING,blank=False,null=False,related_name='iha_address')
    service = models.CharField(
        verbose_name = 'Service',
        max_length=50,
        choices=SERVICE_TYPE,
        blank=False,null=False
    )
    ownership = models.CharField(
        verbose_name = 'Owner Ship',
        max_length=50,
        choices=OWNERSHIP,
        blank=False,null=False
    )
    ownership_other = models.CharField(
        max_length=50,
        blank=True,null=True
    )
    description = models.OneToOneField(Description, on_delete=models.DO_NOTHING,blank=False,null=False,related_name='iha_description')
    
    focusIndustry = ArrayField(models.CharField(
        
        # choices=SECTORS,
        max_length=500),default=list,verbose_name='Focus Industry',
        )
    

    level = ArrayField(models.CharField(
        max_length=500,
        # choices=STARTUP_STAGE,
        # read_only=False,
    ),size=20,default=list,verbose_name='Level',)
    funded_by = models.CharField(
        verbose_name = 'Funded By',
        max_length=50,
        choices=FUNDED_BY_CHOICES,
        blank=False,null=False
    )
    funded_by_other = models.CharField(max_length=50,blank=False,null=False)
    program_duration = models.CharField(
        verbose_name = 'Program Duration',
        max_length=50,
        choices=PROGRAM_DURATION,
        blank=True,null=True
    )
    attachments = models.FileField(upload_to='incubetor/attachments',blank=True,null=True,help_text="please upload relevant documents max 10")
    profile = models.OneToOneField(Profile, on_delete=models.DO_NOTHING,blank=False,null=False,related_name='iha_address')
    @property
    def is_pending(self):
        return self
    def __str__(self):
        return self.description.name.__str__()
    def get_my_model_name(self):
        return self._meta.model_name


class Government(models.Model):
    address = models.OneToOneField(Address, on_delete=models.DO_NOTHING,blank=False,null=False,related_name='Government_address')
    GOVERNMENT_TYPE = models.CharField(
        verbose_name = 'Government type',
        max_length=50,
        choices=GOVERNMENT_TYPE,
        blank=False,null=False
    )
    GOVERNMENT_TYPE_other = models.CharField(
        max_length=50,blank=False,null=False)
    level = ArrayField(models.CharField(
        max_length=500,
        # choices=STARTUP_STAGE,
        # read_only=False,
    ),size=20,default=list)
    
    description = models.OneToOneField(Description, on_delete=models.DO_NOTHING,blank=False,null=False,related_name='Government_description')
    profile = models.OneToOneField(Profile, on_delete=models.DO_NOTHING,blank=False,null=False)
    @property
    def is_pending(self):
        return self
    def __str__(self):
        return self.description.name


class Connect(models.Model):
    requester = models.ForeignKey(User, related_name='requester', on_delete=models.CASCADE,)
    responser = models.ForeignKey(User, related_name='responser', on_delete=models.CASCADE,)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.to_user + self.from_user  
    STATUS_CHOICES = (
        (1, 'Pending'),
        (2, 'Accepted'),
        (3, 'Rejected'),
    )
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    status_admin = models.IntegerField(choices=STATUS_CHOICES, default=1)
    def __str__(self):
        return "From {}, to {}".format(self.requester.username, self.responser.username)
    def get_my_model_name(self):
        return self._meta.model_name

    
 
# python manage.py makemigrations your_app_name --empty

class Carousel(models.Model):
    description = models.CharField(
        verbose_name = 'Description',
        max_length=50,blank=True,null=True)
    svg = models.FileField(
        verbose_name = 'svg',
        upload_to='description/svg',blank=True,null=True, help_text="please upload relevant documents max 10")




class Message(models.Model):
    sender = models.ForeignKey(User, related_name='message_sender_user', verbose_name='user', on_delete=models.CASCADE)
    message = models.TextField()  # Remove max_length or set it to a suitable value
    recipients = models.ManyToManyField(User, related_name='received_messages', blank=True)
    creation_date = models.DateTimeField('Creation date', auto_now_add=True)
    disabled = models.BooleanField(default=False)

    def __str__(self):
        return self.message  # Return the message content as the string representation

    class Meta:
        verbose_name = 'message'
        verbose_name_plural = 'messages'
        # ordering = ('creation_date',)
    def get_recipient_ids(self):
        return list(self.recipients.values_list('id', flat=True))


class Poster(models.Model):
    name = models.CharField(verbose_name='name',max_length=500)
    email = models.EmailField(verbose_name="email",max_length=500)
    subject = models.CharField(verbose_name='subject',max_length=500)
    message = models.TextField(verbose_name="message",max_length=500)
    disabled = models.BooleanField(default=False,max_length=500)

    # def __unicode__(self):
    #     return "Poster"
    
    class Meta:
        verbose_name = ('poster')
        verbose_name_plural = ('posters')




