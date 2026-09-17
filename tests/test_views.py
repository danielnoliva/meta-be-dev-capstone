from django.test import TestCase
from django.urls import reverse

from restaurant.models import Menu
from restaurant.serializers import MenuItemSerializer


class MenuViewTest(TestCase):
    def setUp(self):
        Menu.objects.create(title="Pasta", price="12.99", inventory=10)
        Menu.objects.create(title="Pizza", price="15.50", inventory=8)
        Menu.objects.create(title="Salad", price="7.25", inventory=12)

    def test_getall(self):
        response = self.client.get(reverse("menu"))
        menus = Menu.objects.all()
        serialized_data = MenuItemSerializer(menus, many=True).data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 3)
        self.assertEqual(response.json(), serialized_data)
