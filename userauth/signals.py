import logging
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Booking, Services, Customer
from .utils import update_loyalty_record

# Setup logger
logger = logging.getLogger(__name__)

# Signal for main services
@receiver(m2m_changed, sender=Booking.services.through)
def update_loyalty_records_on_services(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        logger.info(f"Signal triggered for booking ID {instance.id} (services) with services {pk_set}")
        
        
        if not hasattr(instance, 'customer') or instance.customer is None:
            logger.warning(f"No customer linked to booking {instance.id}")
            return

        customer = instance.customer

        for service_id in pk_set:
            try:
                service = Services.objects.get(id=service_id)
                update_loyalty_record(customer, service)
            except Services.DoesNotExist:
                logger.warning(f"Service with ID {service_id} not found")

         


@receiver(m2m_changed, sender=Booking.additional_services.through)
def update_loyalty_records_on_additional_services(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        logger.info(f"Signal triggered for booking ID {instance.id} (additional) with services {pk_set}")
        
        # Check if the booking has a linked customer
        if instance.customer:
            customer = instance.customer
        else:
            # Fall back to customer lookup by email
            try:
                customer = Customer.objects.get(email=instance.email)
            except Customer.DoesNotExist:
                logger.warning(f"No customer found with email {instance.email}")
                return  # If customer doesn't exist, exit early

        # If a customer is found, update loyalty records for each service
        for service_id in pk_set:
            try:
                service = Services.objects.get(id=service_id)
                update_loyalty_record(customer, service)
            except Services.DoesNotExist:
                logger.warning(f"Service with ID {service_id} not found")
