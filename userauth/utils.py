# userauth/utils.py
from .models import LoyaltyProgram, LoyaltyRecord 
def update_loyalty_record(customer, service):
    print(f"Updating loyalty for {customer.email} on service {service.name}")
    try:
        loyalty_program = LoyaltyProgram.objects.get(service=service)
    except LoyaltyProgram.DoesNotExist:
        return  # No loyalty program for this service

    loyalty_record, created = LoyaltyRecord.objects.get_or_create(
        customer=customer,
        loyalty=loyalty_program,
        defaults={
            'free_count': 0,
            'service_taken': 0,
            'status': 'Active'
        }
    )

    loyalty_record.service_taken += 1

    if loyalty_record.service_taken % loyalty_program.frequency == 0:
        loyalty_record.free_count += 1

    loyalty_record.save()
