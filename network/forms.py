from django import forms
from django.contrib.auth.hashers import make_password
from .models import Device, Region,MUnit
from .models import User, Event, Duty,Rating
from django.contrib.auth import get_user_model

User = get_user_model()

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    # def clean(self):
    #     username = self.cleaned_data.get('username')
    #     password = self.cleaned_data.get('password')


class UserCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Parol")

    class Meta:
        model = User
        fields = '__all__'

    def save(self, commit=True):
        user = super().save(commit=False)
        # Parolni shifrlash
        user.password = make_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class CreateEventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['theme', 'photo', 'main_body', 'comment_theme', 'comment']
        widgets = {
            'theme': forms.TextInput(attrs={
                'class': 'form-control shadow-sm rounded-3 mb-3',
                'placeholder': 'Tadbir nomini kiriting...',
            }),
            'photo': forms.ClearableFileInput(attrs={
                'class': 'form-control shadow-sm rounded-3 mb-3',
                'accept': 'image/*',  # faqat rasm fayllarini tanlash uchun
            }),
            'main_body': forms.Textarea(attrs={
                'class': 'form-control shadow-sm rounded-3 mb-3',
                'rows': 6,
                'style': 'resize: none; font-size: 15px; line-height: 1.6; padding: 12px;',
                'placeholder': 'Tadbir haqida to‘liq ma’lumot...',
            }),
            'comment_theme': forms.TextInput(attrs={
                'class': 'form-control shadow-sm rounded-3 mb-3',
                'placeholder': 'Izoh mavzusi...',
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control shadow-sm rounded-3 mb-3',
                'rows': 4,
                'style': 'resize: none; font-size: 14px; line-height: 1.5; padding: 10px;',
                'placeholder': 'Izoh matni...',
            }),
        }
        labels = {
            'theme': 'Tadbir nomi',
            'photo': 'Tadbir rasmi',
            'main_body': 'Tadbir haqida',
            'comment_theme': 'Izoh mavzusi',
            'comment': 'Izoh matni',
        }




from django import forms
from .models import Duty
User = get_user_model()

class MultiDutyForm(forms.ModelForm):
    class Meta:
        model = Duty
        fields = ['user_radio', 'user_outlook', 'user_phone', 'date_b', 'date_f']
        widgets = {
            'user_radio': forms.Select(attrs={
                'class': 'form-select shadow-sm rounded-3 mb-3'
            }),
            'user_outlook': forms.Select(attrs={
                'class': 'form-select shadow-sm rounded-3 mb-3'
            }),
            'user_phone': forms.Select(attrs={
                'class': 'form-select shadow-sm rounded-3 mb-3'
            }),
            'date_b': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control shadow-sm rounded-3 mb-3'
            }),
            'date_f': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control shadow-sm rounded-3 mb-3'
            }),
        }
        labels = {
            'user_radio': '📻 Radio bo‘yicha navbatchi',
            'user_outlook': '💻 Outlook bo‘yicha navbatchi',
            'user_phone': '📞 Telefon bo‘yicha navbatchi',
            'date_b': '🗓 Boshlanish sanasi',
            'date_f': '⏰ Tugash sanasi',
        }

    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if current_user and getattr(current_user, 'm_unit', None):
            user_queryset = User.objects.filter(m_unit=current_user.m_unit)
        else:
            user_queryset = User.objects.none()

        # faqat shu hududdagi userlar ko‘rinsin
        self.fields['user_radio'].queryset = user_queryset
        self.fields['user_outlook'].queryset = user_queryset
        self.fields['user_phone'].queryset = user_queryset



from django import forms

class EditEventForm(forms.Form):
    theme = forms.CharField(
        label='Tadbir nomi',
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control shadow-sm rounded-3 mb-3',
            'placeholder': 'Tadbir nomini kiriting...',
        })
    )

    photo = forms.ImageField(
        label='Tadbir rasmi',
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control shadow-sm rounded-3 mb-3',
            'accept': 'image/*',  # faqat rasm fayllari
        })
    )

    main_body = forms.CharField(
        label='Tadbir haqida',
        widget=forms.Textarea(attrs={
            'class': 'form-control shadow-sm rounded-3 mb-3',
            'rows': 6,
            'style': 'resize: none; font-size: 15px; line-height: 1.6; padding: 12px;',
            'placeholder': 'Tadbir haqida to‘liq ma’lumot...',
        })
    )

    comment_theme = forms.CharField(
        label='Izoh mavzusi',
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control shadow-sm rounded-3 mb-3',
            'placeholder': 'Izoh mavzusi...',
        })
    )

    comment = forms.CharField(
        label='Izoh matni',
        widget=forms.Textarea(attrs={
            'class': 'form-control shadow-sm rounded-3 mb-3',
            'rows': 4,
            'style': 'resize: none; font-size: 14px; line-height: 1.5; padding: 10px;',
            'placeholder': 'Izoh matni...',
        })
    )


class EditDutyForm(forms.Form):
    user_radio = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label='📻 Radio bo‘yicha navbatchi',
        widget=forms.Select(attrs={
            'class': 'form-select shadow-sm rounded-3 mb-3'
        })
    )

    user_outlook = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label='💻 Outlook bo‘yicha navbatchi',
        widget=forms.Select(attrs={
            'class': 'form-select shadow-sm rounded-3 mb-3'
        })
    )

    user_phone = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label='📞 Telefon bo‘yicha navbatchi',
        widget=forms.Select(attrs={
            'class': 'form-select shadow-sm rounded-3 mb-3'
        })
    )

    date_b = forms.DateField(
        label='🗓 Boshlanish sanasi',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control shadow-sm rounded-3 mb-3'
        })
    )

    date_f = forms.DateField(
        label='⏰ Tugash sanasi',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control shadow-sm rounded-3 mb-3'
        })
    )


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['score', 'comment']
        widgets = {
            'score': forms.RadioSelect(choices=[(i, f"{i} ⭐") for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Izoh yozing (ixtiyoriy)...'
            }),
        }

class DeviceAdminForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        if request and request.user.is_staff and not request.user.is_superuser:
            self.fields['region'].queryset = Region.objects.filter(
                id=request.user.region.id
            )
        if request and request.user.is_staff and not request.user.is_superuser:
            user_munit = request.user.m_unit

            if user_munit:
                qs = user_munit.can_view_units.all()

                # ❗ agar can_view_units bo‘sh bo‘lsa → o‘zi
                if qs.exists():
                    self.fields['m_unit'].queryset = qs
                else:
                    self.fields['m_unit'].queryset = MUnit.objects.filter(
                        id=user_munit.id
                    )
            else:
                self.fields['m_unit'].queryset = MUnit.objects.none()
