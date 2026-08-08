import os
from datetime import time, timedelta

from django.contrib.sessions.middleware import SessionMiddleware
from django.db.models import Sum, Q
from django.db.models.functions import Coalesce
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.conf import settings

from network.serializers import EventSerializer
from .forms import CreateEventForm, MultiDutyForm, EditEventForm, EditDutyForm, RatingForm, User
from django.contrib import messages

from .forms import LoginForm
from .models import Region, Device, Event, Message, PhoneNumber, Duty, Rating

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB

def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():

            data = form.cleaned_data
            username = data['username']
            password = data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    if request.user.is_superuser:
                        return redirect('index')
                    else: return redirect('index_user')
                else:
                    return render(
                        request,
                        'login.html',
                        {'info': 'Foydalanuvchi aktiv emas', 'form': LoginForm()}
                    )
            else:
                return render(
                    request,
                    'login.html',
                    {'info': 'Login yoki parol xato kiritildi', 'form': LoginForm()}
                )
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def phones(request):
    phones = PhoneNumber.objects.all()
    context = {
        'phones':phones,
    }
    return render(request,'phone_number.html',context)


#=================================================Beginig Views of event=========================================================================
#all events with creation method
@login_required
def events(request):
    edit_id = request.GET.get('edit')

    if request.method == 'POST':
        print("POST paytidagi edit_id == ", edit_id)
        if edit_id:
            ev = Event.objects.get(id=edit_id)
            form = EditEventForm(request.POST, request.FILES)
            if form.is_valid():
                ev.theme = form.cleaned_data['theme']
                ev.photo = form.cleaned_data['photo']
                ev.main_body = form.cleaned_data['main_body']
                ev.comment_theme = form.cleaned_data['comment_theme']
                ev.comment = form.cleaned_data['comment']
                ev.save()
                messages.success(request, "✅ Tadbir muvaffaqiyatli yangilandi!")
                return redirect("events")

        form = CreateEventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user
            event.region = request.user.region
            event.m_unit = request.user.m_unit
            event.communication_node = request.user.communication_node
            event.save()

            messages.success(request, "✅ Tadbir muvaffaqiyatli yaratildi!")

            return redirect("events")

    form = CreateEventForm()
    form1 = EditEventForm()

    user_unit = request.user.m_unit
    visible_units = list(user_unit.can_view_units.all()) + [user_unit]

    today = timezone.localdate()
    yesterday = today - timedelta(days=1)

    events_nd = Event.objects.filter(
        Q(timestamp__date=today) |
        Q(
            timestamp__date=yesterday,
            timestamp__time__gte=time(9, 0)
        ),
        region=request.user.region,
        m_unit__in=visible_units
    ).order_by('-timestamp')

    # Tugallangan tadbirlar (done=True va boshqa shartlar bilan)
    events_d = Event.objects.filter(
        region=request.user.region,
        m_unit__in=visible_units
    ).order_by('-timestamp')
    # events_nd = Event.objects.filter(done=False,region=request.user.region, m_unit__in=visible_units)
    # events_d  = Event.objects.filter(done=True,region=request.user.region, m_unit__in=visible_units)

    print("TADBIRLAR RO'YHATI : ", events_nd)

    context = {
        'events_nd':events_nd,
        'events_d':events_d,
        'user':request.user,
        'form':form,
        'form1':form1,
    }
       
    return render(request,'event.html',context)


@login_required
def eventsAll(request):
    today = timezone.localdate()
    yesterday = today - timedelta(days=1)

    # timestamp DateTimeField bo'lgani uchun sana va vaqtni alohida yoki __date / __time orqali filter qilamiz
    events_nd = Event.objects.filter(
        Q(timestamp__date=today) |
        Q(
            timestamp__date=yesterday,
            timestamp__time__gte=time(9, 0)
        )
    ).order_by('-timestamp')  # Yoki tartiblash uchun boshqa maydon

    events_d = Event.objects.filter(done=True).order_by('-timestamp')

    # print("TADBIRLAR RO'YHATI : ", events_nd)

    context = {
        'events_nd': events_nd,
        'events_d': events_d,
        'user': request.user
    }

    return render(request, 'event-all.html', context)
# def eventsAll(request):
#
#     events_nd = Event.objects.filter
#     events_d = Event.objects.filter(done=True)
#
#     context = {
#         'events_nd': events_nd,
#         'events_d': events_d,
#     }

    return render(request, 'event-all.html', context)
#Ending of one event with id 
def finish_event(request, id):
    if request.method == "POST":
        event = get_object_or_404(Event, id=id)
        event.done = True  # yoki event.is_active = False
        event.save()
        messages.success(request, "✅ Tadbir muvaffaqiyatli tugatildi!")
    return redirect('events')

#=================================================Ending Views of event=========================================================================




@login_required
def access(request):
    return render(request, '403.html')

@login_required
def index(request):
    now = timezone.localtime(timezone.now())
    today = now.date()
    hour = now.hour
    minute = now.minute
    # print('soat-',hour,'minut-',minute,'sana',today)
    # 9:00 dan keyin keyingi kunni ko‘rsatish
    if hour >= 9:
        date_to_check = today
    else:
        # Agar hali 9 bo‘lmasa, kechagi navbatchilar
        from datetime import timedelta
        date_to_check = today - timedelta(days=1)

    duties = Duty.objects.filter(date_b=date_to_check, region=request.user.region, m_unit=request.user.m_unit)

    if not request.user.is_superuser:
        return redirect('access')
        # return HttpResponseForbidden("Sizga ushbu sahifaga ruxsat yo‘q.")
    form = RatingForm(request.POST)
    id = request.GET.get('user_id')
    user = User.objects.filter(id=id).first()
    if form.is_valid():
        rating = form.save(commit=False)
        rating.user = user
        rating.save()
        messages.success(request, "✅ Baholash muvaffaqiyatli yaratildi!")
        return redirect('index')
    regions = Region.objects.all()
    form  = RatingForm()
    context = {
        'form':form,
        'regions': regions,
        'duties': duties,
        'user_obj': request.user,
        'current_time': now,
        'date_to_check': date_to_check
    }
    return render(request, 'index.html', context)

@login_required
def index_user(request):
    now = timezone.localtime(timezone.now())
    today = now.date()
    hour = now.hour
    minute = now.minute
    # print('soat-',hour,'minut-',minute,'sana',today)
    # 9:00 dan keyin keyingi kunni ko‘rsatish
    if hour >= 9:
        date_to_check = today
    else:
        # Agar hali 9 bo‘lmasa, kechagi navbatchilar
        from datetime import timedelta
        date_to_check = today - timedelta(days=1)

    duties = Duty.objects.filter(date_b=date_to_check,region=request.user.region, m_unit=request.user.m_unit)



    if request.user.is_superuser:
        # return HttpResponseForbidden("Faqat viloyat foydalanuvchilari kirishi mumkin")
        return render(request,'407.html',status=403)
    if request.method == 'POST':
        form = MultiDutyForm(request.POST, user=request.user)
        if form.is_valid():
            duty = form.save(commit=False)  # model instance hosil bo‘ladi
            duty.region = request.user.region
            duty.m_unit = request.user.m_unit
            duty.save()
            messages.success(request, "✅ Yangi navbatchilik muvaffaqiyatli qo‘shildi!")
            return redirect('index_user')
        else:
            messages.error(request, f"❌ xatoliklari: {form.errors}")
    form = MultiDutyForm(user=request.user)
    regions = Region.objects.all()

    context = {
        'current_user_region' : request.user.region.name,
        'regions': regions,
        'user_obj': request.user,
        'form': form,

        'duties': duties,
        'current_time': now,
        'date_to_check': date_to_check
    }

    return render(request, 'user_index.html', context)

@login_required
def dutys(request):
    edit_id = request.GET.get('edit')

    if request.method == 'POST':
        print("POST paytidagi edit_id == ", edit_id)
        if edit_id:
            dt = Duty.objects.get(id=edit_id)
            form = EditDutyForm(request.POST, request.FILES)
            if form.is_valid():
                dt.user_radio = form.cleaned_data['user_radio']
                dt.user_phone = form.cleaned_data['user_phone']
                dt.user_outlook = form.cleaned_data['user_outlook']
                dt.date_b = form.cleaned_data['date_b']
                dt.date_f = form.cleaned_data['date_f']
                dt.save()
                messages.success(request, "✅ Navbatchilar muvaffaqiyatli yangilandi!")
                return redirect("dutys")


        form = MultiDutyForm(request.POST, user=request.user)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.region = request.user.region
            obj.m_unit = request.user.m_unit
            obj.save()
            messages.success(request, f"{'Yaratildi ✅'}")
            return redirect('dutys')
        else:
            messages.error(request, "Xatolik yuz berdi ❌")
    else:
        form = MultiDutyForm(user=request.user)
    dutys = Duty.objects.filter(region=request.user.region, m_unit=request.user.m_unit)
    return render(request, 'dutys.html', {

        'form': form,
        'dutys': dutys,
    })







# REGION DATA (all or per region)
@login_required
def api_region_data(request, region_id):
    # region_id == 'all' => all regions
    from django.db.models import Sum

    ratings = {
        r["user"]: r["total_score"]
        for r in Rating.objects.values("user")
        .annotate(total_score=Sum("score"))
    }

    today = timezone.localdate()
    yesterday = today - timedelta(days=1)
    if region_id == 'all':
        devices_qs = Device.objects.all()
        events_qs =Event.objects.filter(
                Q(timestamp__date=today) |
                Q(
                    timestamp__date=yesterday,
                    timestamp__time__gte=time(9, 0)
                ),
            ).order_by('-timestamp')
        users_qs = Duty.objects.select_related("region", "user_outlook", "user_phone", "user_radio"
                                               )

    else:
        today = timezone.localdate()
        yesterday = today - timedelta(days=1)
        devices_qs = Device.objects.filter(region_id=region_id)
        events_qs =Event.objects.filter(
                Q(timestamp__date=today) |
                Q(
                    timestamp__date=yesterday,
                    timestamp__time__gte=time(9, 0)
                ),
                region_id = region_id,
            ).order_by('-timestamp')
        users_qs = Duty.objects.select_related("region", "user_outlook", "user_phone", "user_radio"
                                               )



    total_devices = devices_qs.count()
    active_devices = devices_qs.filter(is_active=True).count()
    inactive_qs = devices_qs.filter(is_active=False)
    inactive_devices = inactive_qs.count()

    device_types = {k: 0 for k, _ in Device._meta.get_field('type').choices}
    for k, _ in Device._meta.get_field('type').choices:
        device_types[k] = devices_qs.filter(type=k).count()

    # events list summary (for modal detailed view we provide endpoint)
    events_list = list(events_qs.values('id', 'theme', 'timestamp', 'user__username','done'))
    users_list = list(users_qs.values(
        'id',
        'date_b',
        'm_unit__name',
        'region__name',

        'user_outlook__id',
        'user_outlook__first_name',
        'user_outlook__last_name',

        'user_phone__id',
        'user_phone__first_name',
        'user_phone__last_name',

        'user_radio__id',
        'user_radio__first_name',
        'user_radio__last_name',
    ))

    for item in users_list:
        item["user_outlook__total_score"] = ratings.get(item["user_outlook__id"], 0)
        item["user_phone__total_score"] = ratings.get(item["user_phone__id"], 0)
        item["user_radio__total_score"] = ratings.get(item["user_radio__id"], 0)


    inactive_list = list(inactive_qs.values('id', 'name', 'ip_address','region__name'))
    percent = int((active_devices / total_devices) * 100) if total_devices > 0 else 100
    current_user_region = request.user.region.name
    # print(events_list)
    data = {
        "total_devices": total_devices,
        "active_devices": active_devices,
        "inactive_devices": inactive_devices,
        "inactive_list": inactive_list,
        "percent": percent,
        "device_types": device_types,
        "total_events": events_qs.count(),
        "total_users": users_qs.count(),
        "events_summary": events_list,
        "users_summary": users_list,
        "current_user_region": current_user_region,
    }
    return JsonResponse(data)

@login_required
def api_region_user_data(request, region_id):
    global timedelta
    user_unit = request.user.m_unit
    visible_units = list(user_unit.can_view_units.all()) + [user_unit]

    now = timezone.localtime(timezone.now())
    today = now.date()
    hour = now.hour
    minute = now.minute
    # print('soat-',hour,'minut-',minute,'sana',today)
    # 9:00 dan keyin keyingi kunni ko‘rsatish
    if hour >= 9:
        date_to_check = today
    else:
        # Agar hali 9 bo‘lmasa, kechagi navbatchilar
        from datetime import timedelta
        date_to_check = today - timedelta(days=1)

    devices_qs = Device.objects.filter(m_unit__in=visible_units)

    today1 = timezone.localdate()
    yesterday = today - timedelta(days=1)

    events_qs = Event.objects.filter(
        Q(timestamp__date=today1) |
        Q(
            timestamp__date=yesterday,
            timestamp__time__gte=time(9, 0)
        ),m_unit__in=visible_units,).order_by('-timestamp')

    users_qs = Duty.objects.select_related("region","user_outlook","user_phone","user_radio"
).filter(date_b=date_to_check)


    region_devices = devices_qs.count()
    active_devices = devices_qs.filter(is_active=True).count()
    inactive_qs = devices_qs.filter(is_active=False)
    inactive_devices = inactive_qs.count()

    device_types = {k: 0 for k, _ in Device._meta.get_field('type').choices}
    for k, _ in Device._meta.get_field('type').choices:
        device_types[k] = devices_qs.filter(type=k).count()

    from django.db.models import Sum

    ratings = {
        r["user"]: r["total_score"]
        for r in Rating.objects.values("user")
        .annotate(total_score=Sum("score"))
    }



    # events list summary (for modal detailed view we provide endpoint)
    events_list = list(events_qs.values('id','user__username', 'theme','m_unit__name','communication_node','region__name','main_body','comment_theme','comment','done','photo', 'timestamp', 'user'))
    region_users_list = list(users_qs.values(
        'id',
        'date_b',
        'm_unit__name',
        'region__name',

        'user_outlook__id',
        'user_outlook__first_name',
        'user_outlook__last_name',

        'user_phone__id',
        'user_phone__first_name',
        'user_phone__last_name',

        'user_radio__id',
        'user_radio__first_name',
        'user_radio__last_name',
    ))

    for item in region_users_list:
        item["user_outlook__total_score"] = ratings.get(item["user_outlook__id"], 0)
        item["user_phone__total_score"] = ratings.get(item["user_phone__id"], 0)
        item["user_radio__total_score"] = ratings.get(item["user_radio__id"], 0)

    inactive_list = list(inactive_qs.values('id', 'name', 'ip_address','region__name'))
    percent = int((active_devices / region_devices) * 100) if region_devices > 0 else 100

    data = {
        "region_devices": region_devices,
        "active_devices": active_devices,
        "inactive_devices": inactive_devices,
        "inactive_list": inactive_list,
        "percent": percent,
        "device_types": device_types,
        "region_events": events_qs.count(),
        "region_users": users_qs.count(),
        "events_summary": events_list,
        "users_summary": region_users_list,

    }
    return JsonResponse(data)


@login_required
def api_event_detail(request, pk):
    ev = get_object_or_404(Event, pk=pk)
    serializer = EventSerializer(ev)
    return JsonResponse(serializer.data, safe=False)



@login_required
def api_chat_list(request):
    if request.method == 'GET':
        msgs = Message.objects.select_related('sender').all()
        data = []
        for m in msgs:
            data.append({
                'id': m.id,
                'sender': m.sender.get_full_name() or m.sender.username,
                'sender_id': m.sender.id,
                'text': m.text,
                'file': m.file.url if m.file else None,
                'created_at': m.created_at.isoformat(),
                'can_edit': m.can_edit(request.user),
            })
        return JsonResponse(data, safe=False)

    if request.method == 'POST':
        text = request.POST.get('text', '')
        f = request.FILES.get('file')
        if f and f.size > MAX_FILE_SIZE:
            return HttpResponseBadRequest("File too large")
        msg = Message.objects.create(sender=request.user, text=text, file=f)
        return JsonResponse({'status': 'ok', 'id': msg.id})




###################### Admin template apis ################################################
# #=======================PATS API==============================================
@login_required
def api_pats_list(request, region_id):
    user_unit = request.user.m_unit
    visible_units = list(user_unit.can_view_units.all()) + [user_unit]
    if region_id == 'all':
        qs = Device.objects.filter(type='PATS')
    else:
        qs = Device.objects.filter(type='PATS', region_id=region_id,m_unit__in=visible_units)

    data = list(qs.values('id', 'name', 'ip_address', 'is_active'))
    return JsonResponse(data, safe=False)


@login_required
def api_pats_detail(request, pk):
    dev = get_object_or_404(Device, pk=pk)
    data = {
        'id': dev.id,
        'name': dev.name,
        'ip_address': dev.ip_address,
        'region': dev.region.name if dev.region else '-',
        'type': dev.type,
        'is_active': dev.is_active,
        'last_checked': dev.last_checked.strftime('%Y-%m-%d %H:%M') if dev.last_checked else '-'
    }
    return JsonResponse(data)

# #=======================ending PATS API==============================================


#=================================================Begining BAZASTANSIYA api=========================================================================
@login_required
def api_baza_stansiya_list(request, region_id):
    user_unit = request.user.m_unit
    visible_units = list(user_unit.can_view_units.all()) + [user_unit]
    if region_id == 'all':
        qs = Device.objects.filter(type='BazaStansiya')
    else:
        qs = Device.objects.filter(type='BazaStansiya', region_id=region_id,m_unit__in=visible_units)

    data = list(qs.values('id', 'name', 'ip_address', 'is_active'))
    print(data)
    return JsonResponse(data, safe=False)


@login_required
def api_baza_stansiya_detail(request, pk):
    dev = get_object_or_404(Device, pk=pk)
    data = {
        'id': dev.id,
        'name': dev.name,
        'ip_address': dev.ip_address,
        'region': dev.region.name if dev.region else '-',
        'type': dev.type,
        'is_active': dev.is_active,
        'last_checked': dev.last_checked.strftime('%Y-%m-%d %H:%M') if dev.last_checked else '-'
    }
    return JsonResponse(data)

#=================================================Ending BAZASTANSIYA api=========================================================================


#=================================================Begining grandstream api =========================================================================
@login_required
def api_gats_list(request, region_id):
    user_unit = request.user.m_unit
    visible_units = list(user_unit.can_view_units.all()) + [user_unit]
    if region_id == 'all':
        qs = Device.objects.filter(type='GATS')
    else:
        qs = Device.objects.filter(type='GATS', region_id=region_id,m_unit__in=visible_units)

    data = list(qs.values('id', 'name', 'ip_address', 'is_active'))
    return JsonResponse(data, safe=False)


@login_required
def api_gats_detail(request, pk):
    dev = get_object_or_404(Device, pk=pk)
    data = {
        'id': dev.id,
        'name': dev.name,
        'ip_address': dev.ip_address,
        'region': dev.region.name if dev.region else '-',
        'type': dev.type,
        'is_active': dev.is_active,
        'last_checked': dev.last_checked.strftime('%Y-%m-%d %H:%M') if dev.last_checked else '-'
    }
    return JsonResponse(data)

#=================================================Ending grandstream api=========================================================================



#=================================================Begining vlan api =========================================================================
@login_required
def api_vlan_list(request, region_id):
    user_unit = request.user.m_unit
    visible_units = list(user_unit.can_view_units.all()) + [user_unit]

    if region_id == 'all':
        qs = Device.objects.filter(type='VLAN')
    else:
        qs = Device.objects.filter(type='VLAN', region_id=region_id,m_unit__in=visible_units)

    data = list(qs.values('id', 'name', 'ip_address', 'is_active'))
    return JsonResponse(data, safe=False)


@login_required
def api_vlan_detail(request, pk):
    dev = get_object_or_404(Device, pk=pk)
    data = {
        'id': dev.id,
        'name': dev.name,
        'ip_address': dev.ip_address,
        'region': dev.region.name if dev.region else '-',
        'type': dev.type,
        'is_active': dev.is_active,
        'last_checked': dev.last_checked.strftime('%Y-%m-%d %H:%M') if dev.last_checked else '-'
    }
    return JsonResponse(data)

#=================================================Ending vlan api=========================================================================





#=================================================Begining duty api =========================================================================
@login_required
def api_duty_list(request, region_id):
    user_unit = request.user.m_unit
    visible_units = list(user_unit.can_view_units.all()) + [user_unit]

    now = timezone.localtime(timezone.now())
    today = now.date()
    hour = now.hour
    minute = now.minute
    # print('soat-',hour,'minut-',minute,'sana',today)
    # 9:00 dan keyin keyingi kunni ko‘rsatish
    if hour >= 9:
        date_to_check = today
    else:
        # Agar hali 9 bo‘lmasa, kechagi navbatchilar
        from datetime import timedelta
        date_to_check = today - timedelta(days=1)

    if region_id == 'all':
        qs = Duty.objects.filter(date_b=date_to_check)
    else:
        qs = Duty.objects.select_related("region","user_outlook","user_phone","user_radio"
).filter(date_b=date_to_check, m_unit__in=visible_units)

    # data = []
    # for d in qs:
    #     data.append({
    #         "id": d.id,
    #         "date_b": d.date_b,
    #         "date_f": d.date_f,
    #
    #         # Region information
    #         # "region_id": d.region.id,
    #         "region_name": d.region.name,
    #
    #         # User Outlook
    #         "user_outlook_id": d.user_outlook.id,
    #         "user_outlook_name": d.user_outlook.username,
    #
    #         # User Phone
    #         "user_phone_id": d.user_phone.id,
    #         "user_phone_name": d.user_phone.username,
    #
    #         # User Radio
    #         "user_radio_id": d.user_radio.id,
    #         "user_radio_name": d.user_radio.username,
    #
    #         "m_unit": d.m_unit.name
    #     })
    data = []
    for d in qs:
        # Radio user score va commentlari
        radio_ratings = d.user_radio.ratings.all()
        radio_score = radio_ratings.aggregate(total_score=Coalesce(Sum('score'), 0))['total_score']
        radio_comments = [r.comment for r in radio_ratings if r.comment]

        # Phone user score va commentlari
        phone_ratings = d.user_phone.ratings.all()
        phone_score = phone_ratings.aggregate(total_score=Coalesce(Sum('score'), 0))['total_score']
        phone_comments = [r.comment for r in phone_ratings if r.comment]

        # Outlook user score va commentlari
        outlook_ratings = d.user_outlook.ratings.all()
        outlook_score = outlook_ratings.aggregate(total_score=Coalesce(Sum('score'), 0))['total_score']
        outlook_comments = [r.comment for r in outlook_ratings if r.comment]

        data.append({
            "id": d.id,
            "date_b": d.date_b,
            "date_f": d.date_f,

            # Region information
            "region_name": d.region.name,

            # User Outlook
            "user_outlook_id": d.user_outlook.id,
            "user_outlook_name": d.user_outlook.username,
            "user_outlook_first_name": d.user_outlook.first_name,
            "user_outlook_last_name": d.user_outlook.last_name,
            "user_outlook_score": outlook_score,
            "user_outlook_comments": outlook_comments,

            # User Phone
            "user_phone_id": d.user_phone.id,
            "user_phone_name": d.user_phone.username,
            "user_phone_first_name": d.user_phone.first_name,
            "user_phone_last_name": d.user_phone.last_name,
            "user_phone_score": phone_score,
            "user_phone_comments": phone_comments,

            # User Radio
            "user_radio_id": d.user_radio.id,
            "user_radio_name": d.user_radio.username,
            "user_radio_first_name": d.user_radio.first_name,
            "user_radio_last_name" : d.user_radio.last_name,
            "user_radio_score": radio_score,
            "user_radio_comments": radio_comments,

            "m_unit": d.m_unit.name
        })

    print(data)
    return JsonResponse(data, safe=False)


@login_required
def api_duty_detail(request, pk):
    user = get_object_or_404(User, pk=pk)

    ratings = user.ratings.all()  # Barcha ratinglar

    total_score = ratings.aggregate(total=Coalesce(Sum('score'), 0))['total']

    # Har bir comment va score ro'yxati
    comments_with_score = []
    for r in ratings:
        if r.comment:  # bo'sh commentlarni chiqarib tashlash
            comments_with_score.append({
                'comment': r.comment,
                'score': r.score
            })

    data = {
        'id': user.id,
        'username': user.username,
        'photo': user.photo.url if user.photo else None,
        'total_score': total_score,
        'comments': comments_with_score,
    }

    return JsonResponse(data)

#=================================================Ending duty api=========================================================================



#=================================================Begining ABONENT api =========================================================================
@login_required
def api_abonent_list(request, region_id):
    user_unit = request.user.m_unit
    visible_units = list(user_unit.can_view_units.all()) + [user_unit]

    if region_id == 'all':
        qs = Device.objects.filter(type='Abonent')
    else:
        qs = Device.objects.filter(type='Abonent', region_id=region_id,m_unit__in=visible_units)

    data = list(qs.values('id', 'name', 'ip_address', 'is_active'))
    return JsonResponse(data, safe=False)


@login_required
def api_abonent_detail(request, pk):
    dev = get_object_or_404(Device, pk=pk)
    data = {
        'id': dev.id,
        'name': dev.name,
        'ip_address': dev.ip_address,
        'region': dev.region.name if dev.region else '-',
        'type': dev.type,
        'is_active': dev.is_active,
        'last_checked': dev.last_checked.strftime('%Y-%m-%d %H:%M') if dev.last_checked else '-'
    }
    return JsonResponse(data)

#=================================================Ending ABONENT api=========================================================================





#=================================================Begining firewall api =========================================================================
@login_required
def api_firewall_list(request, region_id):
    print('region id == ',region_id)
    if region_id == 'all':
        qs = Device.objects.filter(type='Firewall')
    else:
        # qs = Device.objects.filter(type='Firewall', region_id=region_id,m_unit=request.user.m_unit)
        qs = Device.objects.filter(type='Firewall',region_id=region_id)
        print('qs -',qs)

    data = list(qs.values('id', 'name', 'ip_address', 'is_active'))
    print('firewall == ',data)
    return JsonResponse(data, safe=False)


@login_required
def api_firewall_detail(request, pk):
    dev = get_object_or_404(Device, pk=pk)
    data = {
        'id': dev.id,
        'name': dev.name,
        'ip_address': dev.ip_address,
        'region': dev.region.name if dev.region else '-',
        'type': dev.type,
        'is_active': dev.is_active,
        'last_checked': dev.last_checked.strftime('%Y-%m-%d %H:%M') if dev.last_checked else '-'
    }
    return JsonResponse(data)

#=================================================Ending Firewall api=========================================================================

























###################### User template apis ################################################
# #=======================PATS API==============================================
@login_required
def api_pats_list_user(request, region_id):
    user_unit = request.user.m_unit
    visible_units = list(user_unit.can_view_units.all()) + [user_unit]
    if region_id == 'all':
        qs = Device.objects.filter(type='PATS')
    else:
        qs = Device.objects.filter(type='PATS', m_unit__in=visible_units)

    data = list(qs.values('id', 'name', 'ip_address', 'is_active'))
    return JsonResponse(data, safe=False)


@login_required
def api_pats_detail_user(request, pk):
    dev = get_object_or_404(Device, pk=pk)
    data = {
        'id': dev.id,
        'name': dev.name,
        'ip_address': dev.ip_address,
        'region': dev.region.name if dev.region else '-',
        'type': dev.type,
        'is_active': dev.is_active,
        'last_checked': dev.last_checked.strftime('%Y-%m-%d %H:%M') if dev.last_checked else '-'
    }
    return JsonResponse(data)

# #=======================ending PATS API==============================================


#=================================================Begining BAZASTANSIYA api=========================================================================
@login_required
def api_baza_stansiya_list_user(request, region_id):
    user_unit = request.user.m_unit
    visible_units = list(user_unit.can_view_units.all()) + [user_unit]
    if region_id == 'all':
        qs = Device.objects.filter(type='BazaStansiya')
    else:
        qs = Device.objects.filter(type='BazaStansiya',m_unit__in=visible_units)

    data = list(qs.values('id', 'name', 'ip_address', 'is_active'))
    print(data)
    return JsonResponse(data, safe=False)


@login_required
def api_baza_stansiya_detail_user(request, pk):
    dev = get_object_or_404(Device, pk=pk)
    data = {
        'id': dev.id,
        'name': dev.name,
        'ip_address': dev.ip_address,
        'region': dev.region.name if dev.region else '-',
        'type': dev.type,
        'is_active': dev.is_active,
        'last_checked': dev.last_checked.strftime('%Y-%m-%d %H:%M') if dev.last_checked else '-'
    }
    return JsonResponse(data)

#=================================================Ending BAZASTANSIYA api=========================================================================




#=================================================Begining grandstream api =========================================================================
@login_required
def api_gats_list_user(request, region_id):
    user_unit = request.user.m_unit
    visible_units = list(user_unit.can_view_units.all()) + [user_unit]
    if region_id == 'all':
        qs = Device.objects.filter(type='GATS')
    else:
        qs = Device.objects.filter(type='GATS', m_unit__in=visible_units)

    data = list(qs.values('id', 'name', 'ip_address', 'is_active'))
    return JsonResponse(data, safe=False)


@login_required
def api_gats_detail_user(request, pk):
    dev = get_object_or_404(Device, pk=pk)
    data = {
        'id': dev.id,
        'name': dev.name,
        'ip_address': dev.ip_address,
        'region': dev.region.name if dev.region else '-',
        'type': dev.type,
        'is_active': dev.is_active,
        'last_checked': dev.last_checked.strftime('%Y-%m-%d %H:%M') if dev.last_checked else '-'
    }
    return JsonResponse(data)

#=================================================Ending grandstream api=========================================================================




#=================================================Begining vlan api =========================================================================
@login_required
def api_vlan_list_user(request, region_id):
    user_unit = request.user.m_unit
    visible_units = list(user_unit.can_view_units.all()) + [user_unit]

    if region_id == 'all':
        qs = Device.objects.filter(type='VLAN')
    else:
        qs = Device.objects.filter(type='VLAN',m_unit__in=visible_units)


    data = list(qs.values('id', 'name', 'ip_address', 'is_active'))
    return JsonResponse(data, safe=False)


@login_required
def api_vlan_detail_user(request, pk):
    dev = get_object_or_404(Device, pk=pk)
    data = {
        'id': dev.id,
        'name': dev.name,
        'ip_address': dev.ip_address,
        'region': dev.region.name if dev.region else '-',
        'type': dev.type,
        'is_active': dev.is_active,
        'last_checked': dev.last_checked.strftime('%Y-%m-%d %H:%M') if dev.last_checked else '-'
    }
    return JsonResponse(data)

#=================================================Ending vlan api=========================================================================





#=================================================Begining duty api =========================================================================
@login_required
def api_duty_list_user(request, region_id):
    user_unit = request.user.m_unit
    visible_units = list(user_unit.can_view_units.all()) + [user_unit]

    now = timezone.localtime(timezone.now())
    today = now.date()
    hour = now.hour
    minute = now.minute
    # print('soat-',hour,'minut-',minute,'sana',today)
    # 9:00 dan keyin keyingi kunni ko‘rsatish
    if hour >= 9:
        date_to_check = today
    else:
        # Agar hali 9 bo‘lmasa, kechagi navbatchilar
        from datetime import timedelta
        date_to_check = today - timedelta(days=1)

    if region_id == 'all':
        qs = Duty.objects.filter(date_b=date_to_check)
    else:
        qs = Duty.objects.select_related("region","user_outlook","user_phone","user_radio"
).filter(date_b=date_to_check, m_unit__in=visible_units)

    # data = []
    # for d in qs:
    #     data.append({
    #         "id": d.id,
    #         "date_b": d.date_b,
    #         "date_f": d.date_f,
    #
    #         # Region information
    #         # "region_id": d.region.id,
    #         "region_name": d.region.name,
    #
    #         # User Outlook
    #         "user_outlook_id": d.user_outlook.id,
    #         "user_outlook_name": d.user_outlook.username,
    #
    #         # User Phone
    #         "user_phone_id": d.user_phone.id,
    #         "user_phone_name": d.user_phone.username,
    #
    #         # User Radio
    #         "user_radio_id": d.user_radio.id,
    #         "user_radio_name": d.user_radio.username,
    #
    #         "m_unit": d.m_unit.name
    #     })
    data = []
    for d in qs:
        # Radio user score va commentlari
        radio_ratings = d.user_radio.ratings.all()
        radio_score = radio_ratings.aggregate(total_score=Coalesce(Sum('score'), 0))['total_score']
        radio_comments = [r.comment for r in radio_ratings if r.comment]

        # Phone user score va commentlari
        phone_ratings = d.user_phone.ratings.all()
        phone_score = phone_ratings.aggregate(total_score=Coalesce(Sum('score'), 0))['total_score']
        phone_comments = [r.comment for r in phone_ratings if r.comment]

        # Outlook user score va commentlari
        outlook_ratings = d.user_outlook.ratings.all()
        outlook_score = outlook_ratings.aggregate(total_score=Coalesce(Sum('score'), 0))['total_score']
        outlook_comments = [r.comment for r in outlook_ratings if r.comment]

        data.append({
            "id": d.id,
            "date_b": d.date_b,
            "date_f": d.date_f,

            # Region information
            "region_name": d.region.name,

            # User Outlook
            "user_outlook_id": d.user_outlook.id,
            "user_outlook_name": d.user_outlook.username,
            "user_outlook_score": outlook_score,
            "user_outlook_comments": outlook_comments,

            # User Phone
            "user_phone_id": d.user_phone.id,
            "user_phone_name": d.user_phone.username,
            "user_phone_score": phone_score,
            "user_phone_comments": phone_comments,

            # User Radio
            "user_radio_id": d.user_radio.id,
            "user_radio_name": d.user_radio.username,
            "user_radio_score": radio_score,
            "user_radio_comments": radio_comments,

            "m_unit": d.m_unit.name
        })

    print(data)
    return JsonResponse(data, safe=False)


@login_required
def api_duty_detail_user(request, pk):
    user = get_object_or_404(User, pk=pk)

    ratings = user.ratings.all()  # Barcha ratinglar

    total_score = ratings.aggregate(total=Coalesce(Sum('score'), 0))['total']

    # Har bir comment va score ro'yxati
    comments_with_score = []
    for r in ratings:
        if r.comment:  # bo'sh commentlarni chiqarib tashlash
            comments_with_score.append({
                'comment': r.comment,
                'score': r.score
            })

    data = {
        'id': user.id,
        'username': user.username,
        'photo': user.photo.url if user.photo else None,
        'total_score': total_score,
        'comments': comments_with_score,
    }

    return JsonResponse(data)

#=================================================Ending duty api=========================================================================



#=================================================Begining ABONENT api =========================================================================
@login_required
def api_abonent_list_user(request, region_id):
    user_unit = request.user.m_unit
    visible_units = list(user_unit.can_view_units.all()) + [user_unit]

    if region_id == 'all':
        qs = Device.objects.filter(type='Abonent')
    else:
        qs = Device.objects.filter(type='Abonent',m_unit__in=visible_units)

    data = list(qs.values('id', 'name', 'ip_address', 'is_active'))
    return JsonResponse(data, safe=False)


@login_required
def api_abonent_detail_user(request, pk):
    dev = get_object_or_404(Device, pk=pk)
    data = {
        'id': dev.id,
        'name': dev.name,
        'ip_address': dev.ip_address,
        'region': dev.region.name if dev.region else '-',
        'type': dev.type,
        'is_active': dev.is_active,
        'last_checked': dev.last_checked.strftime('%Y-%m-%d %H:%M') if dev.last_checked else '-'
    }
    return JsonResponse(data)

#=================================================Ending ABONENT api=========================================================================





#=================================================Begining firewall api =========================================================================
@login_required
def api_firewall_list_user(request, region_id):
    print('region id == ',region_id)
    user_unit = request.user.m_unit
    visible_units = list(user_unit.can_view_units.all()) + [user_unit]

    if region_id == 'all':
        qs = Device.objects.filter(type='Firewall')
    else:
        qs = Device.objects.filter(type='Firewall', m_unit__in=visible_units)
        print('qs -',qs)

    data = list(qs.values('id', 'name', 'ip_address', 'is_active'))
    print('firewall == ',data)
    return JsonResponse(data, safe=False)


@login_required
def api_firewall_detail_user(request, pk):
    dev = get_object_or_404(Device, pk=pk)
    data = {
        'id': dev.id,
        'name': dev.name,
        'ip_address': dev.ip_address,
        'region': dev.region.name if dev.region else '-',
        'type': dev.type,
        'is_active': dev.is_active,
        'last_checked': dev.last_checked.strftime('%Y-%m-%d %H:%M') if dev.last_checked else '-'
    }
    return JsonResponse(data)

#=================================================Ending Firewall api=========================================================================