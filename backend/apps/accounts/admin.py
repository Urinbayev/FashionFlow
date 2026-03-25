"""
Account admin configuration.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, StyleProfile, Address


class StyleProfileInline(admin.StackedInline):
    model = StyleProfile
    can_delete = False
    verbose_name_plural = "Style Profile"
    fk_name = "user"


class AddressInline(admin.TabularInline):
    model = Address
    extra = 0


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["email", "first_name", "last_name", "is_influencer", "is_staff", "created_at"]
    list_filter = ["is_staff", "is_superuser", "is_active", "is_influencer", "gender"]
    search_fields = ["email", "first_name", "last_name", "phone"]
    ordering = ["-created_at"]
    inlines = [StyleProfileInline, AddressInline]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "phone", "date_of_birth", "gender", "avatar")}),
        ("Influencer", {"fields": ("is_influencer", "influencer_code", "influencer_commission_rate")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Status", {"fields": ("email_verified", "marketing_consent")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "first_name", "last_name", "password1", "password2"),
        }),
    )


@admin.register(StyleProfile)
class StyleProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "preferred_fit", "body_type", "sustainability_preference", "updated_at"]
    list_filter = ["preferred_fit", "body_type", "sustainability_preference"]
    search_fields = ["user__email"]
    raw_id_fields = ["user"]


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ["full_name", "user", "address_type", "city", "country", "is_default"]
    list_filter = ["address_type", "country", "is_default"]
    search_fields = ["full_name", "street_address_1", "city", "user__email"]
    raw_id_fields = ["user"]
