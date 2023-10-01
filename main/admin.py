# from django.contrib import admin
# from .models import *


# @admin.register(EthRegion)
# class EthRegionAdmin(admin.ModelAdmin):
#     # list_display = [field.name for field in EthRegion._meta.get_fields()]

#     search_fields = ['region_name']
# @admin.register(Wereda)
# class EthRegionAdmin(admin.ModelAdmin):
#     list_display = [field.name for field in Wereda._meta.get_fields()]
#     search_fields = ['wereda_name','region__region_name']
# @admin.register(Address)
# class Addressdmin(admin.ModelAdmin):
#     list_display = [field.name for field in Address._meta.get_fields()]
#     search_fields = ['country','email','location__wereda_name','phoneNumber','cityName','website',]
# # @admin.register(Profile)
# # class ProfileAdmin(admin.ModelAdmin):
# #     pass
# #     # search_fields = [field.name for field in Profile._meta.fields]
# @admin.register(Startup)
# class StartupAdmin(admin.ModelAdmin):
#     save_as = True
#     pass
# @admin.register(Connect)
# class ConnectAdmin(admin.ModelAdmin):
#     pass
# @admin.register(Description)
# class DescriptionAdmin(admin.ModelAdmin):
#     pass
#     # list_display = [field.name for field in Startup._meta.get_fields()]

# #     search_fields = ['startupName','establishmentYear','sector','stage','marketScope','description',]
# @admin.register(Mentor)
# class MentorAdmin(admin.ModelAdmin):
#     pass
# @admin.register(IncubatorsAccelatorsHub)
# class IncubateLevelsAdmin(admin.ModelAdmin):
#     pass
# # @admin.register(IncubatorsAccelatorsHub)
# # class IncubatorsAccelatorsHubAdmin(admin.ModelAdmin):
# #     pass
# @admin.register(DonorFunder)
# class DonorFunderAdmin(admin.ModelAdmin):
#     pass
# @admin.register(Government)
# class GovernmentAdmin(admin.ModelAdmin):
#     pass

# @admin.register(Profile)
# class ProfileAdmin(admin.ModelAdmin):
#     pass
# # @admin.register(ConnectionList)
# # class ConnectionListAdmin(admin.ModelAdmin):
# #     pass
# # @admin.register(MessageReciver)
# # class MessageReciverAdmin(admin.ModelAdmin):
# #     pass


# from django.contrib import admin
# from .models import *
# # Register your models here.

# # @admin.register(Category)
# # class CategoryAdmin(admin.ModelAdmin):
# #     list_display = ['name','parent','order']
# #     list_filter = ('name',)

# # @admin.register(Profile)
# # class UserProfileDataAdmin(admin.ModelAdmin):
# #     list_display = ['id','user_id','user','birth_date','profile_pic',]
# #     list_filter = ('user', 'birth_date')
# # # @admin.register(Messages)
# # # class MessagesDataAdmin(admin.ModelAdmin):
# #     pass
# # class MessagesDataAdmin(admin.ModelAdmin):
# #     # display datetime in the changelist
# #     list_display = ( 'sender','message_body', 'get_parents','timestamp')
# #     # display datetime when you edit comments
# #     readonly_fields = ('timestamp',)
# #     fields = ( 'sender','message_body', 'reciever','timestamp')
# #     def get_reciver(self,obj):
# #         return "\n".join([p.username for p in obj.reciever.all()])
# #     # optional, use only if you need custom ordering of the fields
    

# admin.site.register(Message)


# # from chats.models import SenderModel, ReceiverModel, ChatModel,ChatKeyModel

# # models = [SenderModel, ReceiverModel,ChatKeyModel]

# # for model in models:
# #     admin.site.register(model)

# # class ChatModelAdmin(admin.ModelAdmin):
# #     # display datetime in the changelist
# #     list_display = ( 'sender','text', 'get_parents','log')
# #     # display datetime when you edit comments
# #     readonly_fields = ('log',)
# #     fields = ( 'sender','text', 'receiver','log')
    
# #     # optional, use only if you need custom ordering of the fields
    

# # admin.site.register(ChatModel, ChatModelAdmin)