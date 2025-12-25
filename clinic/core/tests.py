from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
import json

from .models import Specialization, Doctor


User = get_user_model()


class SpecializationAjaxTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user('staff', 'staff@example.com', 'pass')
        self.staff.is_staff = True
        self.staff.save()

    def test_ajax_detail_and_update(self):
        self.client.force_login(self.staff)
        spec = Specialization.objects.create(name='Cardiology')
        # detail
        url = reverse('api_specialization_detail', args=[spec.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['name'], 'Cardiology')
        # ajax update
        edit_url = reverse('admin_specialization_edit', args=[spec.id])
        resp2 = self.client.post(edit_url, data=json.dumps({'name': 'Cardio'}), content_type='application/json')
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(resp2.json()['name'], 'Cardio')
        spec.refresh_from_db()
        self.assertEqual(spec.name, 'Cardio')


class SpecializationDeleteTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user('staff', 'staff@example.com', 'pass')
        self.staff.is_staff = True
        self.staff.save()

    def test_delete_sets_doctor_specialization_null(self):
        self.client.force_login(self.staff)
        spec = Specialization.objects.create(name='TestSpec')
        doc = Doctor.objects.create(
            name='Dr Test', specialization=spec, experience=5, fees=100, available_days='Mon,Tue', time_slots='9:00 AM',
        )
        delete_url = reverse('admin_specialization_delete', args=[spec.id])
        resp = self.client.post(delete_url)
        self.assertEqual(resp.status_code, 302)
        doc.refresh_from_db()
        self.assertIsNone(doc.specialization)
        # GET should be rejected
        resp2 = self.client.get(delete_url)
        self.assertEqual(resp2.status_code, 400)

