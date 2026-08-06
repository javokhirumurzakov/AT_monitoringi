from django.urls import path
from . import views

urlpatterns = [
    path('',views.user_login, name='login'),

    path('dutys/',views.dutys, name='dutys'),

    path('dashboard/', views.index, name='index'),
    path('monitor-user/', views.index_user, name='index_user'),
    path('logout/', views.user_logout, name='logout'),
    #phones
    path('phones/', views.phones, name='phones'),
     #event
    path('events/', views.events, name='events'),
    path('events-all/', views.eventsAll, name='eventsAll'),
    path("events/finish/<int:id>/", views.finish_event, name="finish_event"),

    # region data
    path('api/region/<str:region_id>/', views.api_region_data, name='api_region_data'),
    path('api/region-user/<str:region_id>/', views.api_region_user_data, name='api_region_user_data'),

    # events
    path('api/events/<int:pk>/', views.api_event_detail, name='api_event_detail'),

    # chat
    path('api/chat/', views.api_chat_list, name='api_chat_list'),

    path('access-denied/', views.access, name='access'),

    # basestations apis
    path('api/bazastansiyalar/<region_id>/', views.api_baza_stansiya_list),
    path('api/bazastansiya/<int:pk>/', views.api_baza_stansiya_detail),

# pats apis
    path('api/patslar/<region_id>/', views.api_pats_list),
    path('api/pats/<int:pk>/', views.api_pats_detail),

# Gats apis
    path('api/gatslar/<region_id>/', views.api_gats_list),
    path('api/gats/<int:pk>/', views.api_gats_detail),

# vlan apis
    path('api/vlanlar/<region_id>/', views.api_vlan_list),
    path('api/vlan/<int:pk>/', views.api_vlan_detail),

# duty apis
    path('api/dutylar/<region_id>/', views.api_duty_list),
    path('api/duty/<int:pk>/', views.api_duty_detail),

# vlan apis
    path('api/abonentlar/<region_id>/', views.api_abonent_list),
    path('api/abonent/<int:pk>/', views.api_abonent_detail),


# firewall apis
    path('api/firewalls/<region_id>/', views.api_firewall_list),
    path('api/firewall/<int:pk>/', views.api_firewall_detail),



######################### user region apis ################################################
    # basestations apis
    path('api/bazastansiyalar_user/<region_id>/', views.api_baza_stansiya_list_user),
    path('api/bazastansiya_user/<int:pk>/', views.api_baza_stansiya_detail_user),

# pats apis
    path('api/patslar_user/<region_id>/', views.api_pats_list_user),
    path('api/pats_user/<int:pk>/', views.api_pats_detail_user),

# Gats apis
    path('api/gatslar_user/<region_id>/', views.api_gats_list_user),
    path('api/gats_user/<int:pk>/', views.api_gats_detail),

# vlan apis
    path('api/vlanlar_user/<region_id>/', views.api_vlan_list_user),
    path('api/vlan_user/<int:pk>/', views.api_vlan_detail_user),

# duty apis
    path('api/dutylar_user/<region_id>/', views.api_duty_list_user),
    path('api/duty_user/<int:pk>/', views.api_duty_detail_user),

# vlan apis
    path('api/abonentlar_user/<region_id>/', views.api_abonent_list_user),
    path('api/abonent_user/<int:pk>/', views.api_abonent_detail_user),


# firewall apis
    path('api/firewalls_user/<region_id>/', views.api_firewall_list_user),
    path('api/firewall_user/<int:pk>/', views.api_firewall_detail_user),
]
