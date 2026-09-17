from django.test import TestCase
from restaurant.models import Booking, Menu

class ModelTestCase(TestCase):
    def test_booking_str(self):
        booking = Booking.objects.create(name="John Doe", number_of_guests=4, booking_date="2023-10-01")
        self.assertEqual(str(booking), "John Doe - 2023-10-01 - 4 guests")

    def test_menu_str(self):
        menu_item = Menu.objects.create(title="Pasta", price=12.99, inventory=10)
        self.assertEqual(str(menu_item), "Pasta : $12.99")