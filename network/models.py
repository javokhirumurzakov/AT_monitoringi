import re

blank_re = re.compile(br'^[ \t\f]*(?:[#\r\n]|$)')

from ckeditor.fields import RichTextField
from django.contrib.auth.hashers import make_password
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

DEVICE_TYPES = [
    ("BazaStansiya", "BazaStansiya"),
    ("Firewall", "Firewall"),
    ("Mikrotik", "Mikrotik"),
    ("PATS", "PATS"),
    ("GATS", "GATS"),
    ("VLAN", "VLAN"),
    ("Abonent", "Abonent"),
]

class Region(models.Model):
    name = models.CharField(max_length=32)
    def __str__(self): return self.name


class MUnit(models.Model):
    name = models.CharField(max_length=100, unique=True)
    can_view_units = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='viewed_by'
    )

    def __str__(self):
        return self.name

class User(AbstractUser):
    communication_node = models.TextField(max_length=60,verbose_name="Aloqa tugun",blank=True,null=True)
    m_unit = models.ForeignKey(MUnit, on_delete=models.SET_NULL, null=True, blank=True,default=None)
    position = models.CharField(max_length=100,blank=True,null=True,verbose_name="Lavozim")
    region = models.ForeignKey(Region,on_delete=models.CASCADE,verbose_name="Hudud nomi",blank=True,null=True)
    rank = models.CharField(max_length=40,blank=True,null=True,verbose_name="Harbiy unvon")
    date_brith = models.DateTimeField(verbose_name="Tugilgan yil",blank=True,null=True)
    photo = models.ImageField(upload_to='profile_pics', blank=True, null=True,verbose_name="Xodim Rasmi",default='profile_pics/user.png')
    phone = models.CharField(max_length=20,blank=True,null=True,verbose_name="Telefon raqam")
    score = models.IntegerField(default=0,verbose_name="Umumiy ball",blank=True,null=True)
    point = models.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)],default=1)
    comment = models.TextField(blank=True,null=True,verbose_name="Foydalnuvchiga izoh")
    timestamp = models.DateTimeField(auto_now_add=True)

    password = models.CharField(max_length=128, verbose_name="Parol")

    def save(self, *args, **kwargs):
        # Parol hashlanganligini tekshiramiz
        if self.password and not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username}"

class Event(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,verbose_name="Xodim")
    theme = models.CharField(max_length=100,verbose_name="Tadbir haqida qisqacha malumot")
    m_unit = models.ForeignKey(MUnit, on_delete=models.SET_NULL, null=True, blank=True,default=None)
    communication_node = models.TextField(max_length=60,verbose_name="Aloqa tugun",blank=True,null=True)
    region = models.ForeignKey(Region,on_delete=models.CASCADE,verbose_name="Hudud nomi")
    photo =  models.ImageField(upload_to='tadbir_images/', blank=True, null=True,verbose_name="Tadbir rasmi")
    main_body = RichTextField(verbose_name="Asosiy qism")
    comment_theme = models.CharField(max_length=300,blank=True,null=True,verbose_name="tadbir mavzusi")
    comment = RichTextField(blank=True,null=True,verbose_name="Tadbirga izoh")
    done = models.BooleanField(default=False)
    timestamp= models.DateTimeField(auto_now_add=True,verbose_name="Tadbir vaqti")

    def can_edit(self, user):
        return user == self.user

    def __str__(self):
        return self.theme

class Device(models.Model):

    name = models.CharField(max_length=100, verbose_name="Qurilma nomi", unique=True,blank=True,null=True)
    type = models.CharField(max_length=30, choices=DEVICE_TYPES,blank=True,null=True)
    ip_address = models.GenericIPAddressField(protocol='IPv4', verbose_name="IP Manzil", unique=True,blank=True,null=True)
    is_active = models.BooleanField(default=False, verbose_name="faollik",blank=True,null=True)
    last_checked = models.DateTimeField(auto_now=True, verbose_name="oxirgi ozgarishlar",blank=True,null=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, verbose_name="Hudud nomi")
    m_unit = models.ForeignKey(MUnit, on_delete=models.SET_NULL, null=True, blank=True,default=None)
    koorX = models.FloatField(blank=True, null=True, verbose_name="X koordinata")
    koorY = models.FloatField(blank=True, null=True, verbose_name="Y koordinata")
    jolashuvi = models.CharField(max_length=60, verbose_name="qurilma jolashgan joyi",blank=True,null=True)
    model = models.CharField(max_length=100, verbose_name="Qurilma model",blank=True,null=True)
    year = models.DateField(blank=True, null=True, verbose_name="yil")
    full_info = RichTextField(verbose_name="toliq malumot",blank=True,null=True)
    javob_shax = RichTextField(verbose_name="javobgar shaxslar va tel raqamlar",blank=True,null=True)
    ichki_nomer = RichTextField(verbose_name="ichki nomerlar",blank=True,null=True)
    comment_theme = models.CharField(blank=True, null=True, max_length=100, verbose_name="izoh mavzusi")
    comment = models.TextField(blank=True, null=True, verbose_name="izoh")  # yozilsa yangi tadbir yaratiladi
    off_times = models.IntegerField(default=0, verbose_name="off times")


    def __str__(self):
        return f"{self.name} ({self.ip_address})"

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    text = models.TextField(blank=True)
    file = models.FileField(upload_to='chat_files/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def can_edit(self, user):
        return self.sender == user


class PhoneDepartment(models.Model):
    name = models.CharField(max_length=100, verbose_name="telefon bolimi nomi")

    def __str__(self):
        return self.name

class PhoneNumber(models.Model):
    fio = models.CharField(max_length=100, verbose_name="telefon egasi fio")
    department = models.ForeignKey(PhoneDepartment, on_delete=models.CASCADE, related_name='phonedepartment')
    panasonic_number = models.CharField(max_length=5, verbose_name="panasonic ")
    zas_number = models.CharField(max_length=5, verbose_name="zas")
    grandstream_number = models.CharField(max_length=5, verbose_name="grandstream")
    city_number = models.CharField(max_length=12, verbose_name="shahar telefon raqami")
    mobile_number = models.CharField(max_length=12, verbose_name="mobile number")

    def __str__(self):
        return f"{self.fio}-{self.panasonic_number}"



class Duty(models.Model):

    user_radio = models.ForeignKey(User, on_delete=models.CASCADE, related_name='duties_radio')
    user_phone = models.ForeignKey(User, on_delete=models.CASCADE, related_name='duties_phone')
    user_outlook = models.ForeignKey(User, on_delete=models.CASCADE, related_name='duties_outlook')
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='duties_region')
    date_b = models.DateField()
    date_f = models.DateField()
    m_unit = models.ForeignKey(MUnit, on_delete=models.SET_NULL, null=True, blank=True,default=None)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Navbatchi - {self.user_radio.username} {self.region.name}"



class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    score = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.user.username} — {self.score}⭐"