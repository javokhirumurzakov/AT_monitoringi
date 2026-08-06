from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from .models import Region

from .forms import UserCreateForm,DeviceAdminForm
from .models import *


class HiddenAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return request.user.is_superuser  # faqat superuser ko‘radi


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    add_form = UserCreateForm
    form = UserCreateForm
    edit_form = UserCreateForm
    list_display = ('username', 'region','m_unit', 'is_staff', 'is_superuser','password')

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('id','name')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('id','user','region','m_unit','theme','timestamp','done')

# @admin.register(Device)
# class DeviceAdmin(admin.ModelAdmin):
#     list_display = ('name','region','m_unit','ip_address','is_active')
#
#     #✅ Faqatoz regionidagi devicelarni ko‘rsat
#
#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         if request.user.is_superuser:
#             return qs
#         if request.user.is_staff and request.user.region:
#             return qs.filter(region=request.user.region)
#         return qs.none()
#
#     # ✅ Yangi device yaratayotganda regionni avtomatik o‘ziga bog‘la
#     def save_model(self, request, obj, form, change):
#         if not request.user.is_staff and request.user.region:
#             obj.region = request.user.region
#         super().save_model(request, obj, form, change)
#
#     # ✅ O‘zgartirish faqat o‘z regionidagi device bo‘lsa
#     def has_change_permission(self, request, obj=None):
#         if request.user.is_staff:
#             return True
#         if obj is None:
#             return True
#         return obj.region == request.user.region
#
#     # ✅ O‘chirish faqat o‘z regionidagi device bo‘lsa
#     def has_delete_permission(self, request, obj=None):
#         if request.user.is_staff:
#             return True
#         if obj is None:
#             return True
#         return obj.region == request.user.region
#
#     # ✅ Faqat Device modeliga ruxsat beramiz
#     def has_module_permission(self, request):
#         return True  # faqat Device moduli ko‘rinsin

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    form = DeviceAdminForm
    list_display = ('name','region','m_unit','ip_address','is_active')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.is_staff and request.user.region:
            return qs.filter(region=request.user.region)
        return qs.none()

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser and request.user.region:
            obj.region = request.user.region
        if request.user.is_staff and not request.user.is_superuser:
            user_munit = request.user.m_unit
            allowed_units = user_munit.can_view_units.all()

            if allowed_units.exists():
                if obj.m_unit not in allowed_units:
                    raise ValidationError(
                        "Sizga bu MUnitni tanlashga ruxsat yo‘q"
                    )
            else:
                # ❗ can_view_units yo‘q → majburan o‘zi
                obj.m_unit = user_munit
        super().save_model(request, obj, form, change)

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return True
        return request.user.is_staff and obj.region == request.user.region

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return True
        return request.user.is_staff and obj.region == request.user.region

    def has_add_permission(self, request):
        return request.user.is_staff

    def has_module_permission(self, request):
        return True

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "region":
            if request.user.is_staff and not request.user.is_superuser:
                kwargs["queryset"] = Region.objects.filter(id=request.user.region.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        AdminForm = super().get_form(request, obj, **kwargs)

        class AdminFormWithRequest(AdminForm):
            def __new__(cls, *args, **kwargs2):
                kwargs2['request'] = request
                return AdminForm(*args, **kwargs2)

        return AdminFormWithRequest


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender','text','file','created_at')

@admin.register(PhoneDepartment)
class PhoneDepartmentAdmin(admin.ModelAdmin):
    list_display = ('id','name')

@admin.register(PhoneNumber)
class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = ('id','fio','department','panasonic_number','zas_number','grandstream_number','city_number','mobile_number')

@admin.register(Duty)
class DutyAdmin(admin.ModelAdmin):
    list_display = ('id','user_radio','user_phone','user_outlook','date_b','date_f','m_unit','created_at')

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('id','user','score','comment','created_at')


@admin.register(MUnit)
class MUnitAdmin(admin.ModelAdmin):
    list_display = ('name',)
    filter_horizontal = ('can_view_units',)  # ko‘p tanlovli maydon uchun


