import re
from django import forms
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.admin import SimpleListFilter
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext as _
from user.models import Profile

unicode_username = forms.RegexField(label=_("Username"), max_length=30,
        regex=re.compile(r'^[\w.@+-]{4,}$', re.U),
        help_text = _("Required. 30 characters or fewer. Alphanumeric \
characters only (letters, digits and underscores)."),
        error_message = _("This value must contain only letters, \
numbers and underscores.")) 

class ProfileAdmin(admin.StackedInline):
    model = Profile
    extra = 0
    max_num = 1
    exclude = ('avatar_uri', )

# Overrides django.contrib.auth.forms.UserCreationForm and changes 
# username to accept a wider range of character in the username. 
class UserCreationForm(UserCreationForm):
    username = unicode_username

# Overrides django.contrib.auth.forms.UserChangeForm and changes 
# username to accept a wider range of character in the username. 
class UserChangeForm(UserChangeForm): 
    username = unicode_username


class CandidateListFilter(SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('is candidate')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'candidate'

    def lookups(self, request, model_admin):
        return (
            (0, _('Yes')),
            (1, _('No')),
        )

    def queryset(self, request, queryset):
        if self.value() == None:
            return queryset
        return queryset.filter(candidate__isnull=bool(int(self.value())))


class UnicodeUserAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    inlines = [ProfileAdmin, ]
    list_filter = ('is_superuser', 'is_staff', 'profile__is_editor', CandidateListFilter, 'is_active', 'date_joined', 'profile__locality')

admin.site.unregister(User)
admin.site.register(User, UnicodeUserAdmin)
