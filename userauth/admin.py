from django.utils.html import format_html
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from datetime import datetime
from django.contrib import admin
from django.contrib.admin import  SimpleListFilter,DateFieldListFilter
from .models import Customer,Services,Booking,LoyaltyProgram,LoyaltyRecord,ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'sent_at','message')
    search_fields = ('name', 'email', 'message')

@admin.register(Services)
class ServicesAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'get_category_display', 'service_image_tag')
    search_fields = ('name',)
    list_filter = ('category',)
    
    # Add custom method to display service image in the admin list
    def service_image_tag(self, obj):
        if obj.service_img:
            return format_html('<img src="{}" style="height: 50px; border-radius: 5px;" />', obj.service_img.url)
        return "No Image"
    service_image_tag.short_description = 'Image'

    # Add a custom method to show category name in admin
    def get_category_display(self, obj):
        return obj.get_category_display()   
    get_category_display.short_description = 'Category'


admin.site.site_header="Custon Admin"
admin.site.site_title="Custon Admin"    

 
class BookingMonthYearFilter(SimpleListFilter):
    title = _('Date (Month & Year)')
    parameter_name = 'month_year'

    def lookups(self, request, model_admin):
        dates = Booking.objects.dates('date', 'month', order='DESC')
        return [
            (date.strftime("%Y-%m"), date.strftime("%B %Y"))
            for date in dates
        ]

    def queryset(self, request, queryset):
        if self.value():
            try:
                year, month = map(int, self.value().split("-"))
                return queryset.filter(date__year=year, date__month=month)
            except ValueError:
                return queryset
        return queryset

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone_number', 'formatted_date', 'time', 'get_all_services']
    search_fields = ('name', 'email', 'phone_number', 'date')
    
    def formatted_date(self, obj):
        return format_html(
            '<div style="white-space: nowrap; min-width: 100px;">{}</div>',
            obj.date.strftime('%B %d, %Y')
        )
    formatted_date.short_description = 'Date'

     

    list_filter = [  
        BookingMonthYearFilter          
    ]
    date_hierarchy = 'date'  

    def get_all_services(self, obj):
        return ", ".join(
            [s.name for s in obj.services.all()] +
            [s.name for s in obj.additional_services.all()]
        )
    get_all_services.short_description = 'All Services'

     
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email']  
    search_fields = ['name', 'email']       
    list_filter = ['email']     
    def total_services(self, obj):
        return LoyaltyRecord.objects.filter(customer=obj).aggregate(total=sum('service_taken'))['total'] or 0

    total_services.short_description = 'Total Services Taken'

@admin.register(LoyaltyProgram)
class LoyaltyProgramAdmin(admin.ModelAdmin):
    list_display = ('service_name', 'frequency', 'free_fequency')
    search_fields = ('service__name',)
    list_filter = ('frequency', 'free_fequency')

    def service_name(self, obj):
        return obj.service.name
    service_name.short_description = 'Service'


@admin.register(LoyaltyRecord)
class LoyaltyRecordAdmin(admin.ModelAdmin):
    list_display = (
        'customer_name',
        'service_name',
        'service_taken',
        'free_count',
        'is_eligible',
        'status',
    )
    list_select_related = ('customer', 'loyalty', 'loyalty__service') 
    search_fields = ['customer__name']
    list_filter=['customer']  
     

    def customer_name(self, obj):
        return obj.customer.name
    customer_name.short_description = "Customer Name"

    def service_name(self, obj):
        return obj.loyalty.service.name  # Directly get service name via loyalty
    service_name.short_description = "Service"

    def is_eligible(self, obj):
        return obj.service_taken >= obj.loyalty.frequency
    is_eligible.boolean = True
    is_eligible.short_description = "Eligible for Free Service"


