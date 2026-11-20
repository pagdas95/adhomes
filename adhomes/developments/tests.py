import time

from django.core import mail
from django.core import signing
from django.core.cache import cache
from django.test import TestCase
from django.test import override_settings
from django.urls import reverse

from .forms import _TS_SALT
from .models import Lead
from .models import Project
from .models import Property

FROM = '"A.D Homeshelter" <info@adhomeshelder.com>'


def ts(seconds_ago=10):
    return signing.TimestampSigner(salt=_TS_SALT).sign(str(int(time.time()) - seconds_ago))


@override_settings(
    DEFAULT_FROM_EMAIL=FROM,
    LEADS_NOTIFY_EMAIL="leads@example.com",
    LEADS_RATE_LIMIT=5,
)
class LeadCreateTests(TestCase):
    url = reverse("developments:lead_create")

    def setUp(self):
        cache.clear()
        self.project = Project.objects.create(name="Livadia Apartments")
        self.unit = Property.objects.create(project=self.project, name="Apartment 201")

    def post(self, ajax=False, **overrides):
        data = {
            "name": "John Smith",
            "email": "john@example.com",
            "phone": "99123456",
            "message": "Hello",
            "ts": ts(),
            "website": "",
            "next": "/projects/",
        }
        data.update(overrides)
        headers = {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"} if ajax else {}
        return self.client.post(self.url, data, **headers)

    # --- saving + email -------------------------------------------------
    def test_general_enquiry_saves_and_emails(self):
        resp = self.post()
        self.assertRedirects(resp, "/projects/", fetch_redirect_response=False)
        lead = Lead.objects.get()
        self.assertEqual(lead.status, Lead.Status.NEW)
        self.assertEqual(len(mail.outbox), 1)
        msg = mail.outbox[0]
        self.assertEqual(msg.subject, "New contact request from John Smith")
        self.assertEqual(msg.from_email, FROM)
        self.assertEqual(msg.to, ["leads@example.com"])
        self.assertEqual(msg.reply_to, ["john@example.com"])
        self.assertIn("Phone: 99123456", msg.body)

    def test_property_request_subject_and_link(self):
        self.post(property=self.unit.pk)
        lead = Lead.objects.get()
        self.assertEqual(lead.property, self.unit)
        self.assertEqual(lead.project, self.project)  # filled in from the unit
        msg = mail.outbox[0]
        self.assertEqual(msg.subject, "Viewing request for Apartment 201 from John Smith")
        self.assertIn("http://testserver" + self.unit.get_absolute_url(), msg.body)

    def test_project_enquiry_subject(self):
        self.post(project=self.project.pk)
        self.assertEqual(
            mail.outbox[0].subject, "Enquiry about Livadia Apartments from John Smith",
        )

    def test_ajax_returns_json(self):
        resp = self.post(ajax=True)
        self.assertEqual(resp.json()["ok"], True)

    def test_invalid_form_saves_nothing(self):
        resp = self.post(ajax=True, email="not-an-email")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("email", resp.json()["errors"])
        self.assertFalse(Lead.objects.exists())

    def test_email_failure_keeps_lead(self):
        with override_settings(EMAIL_BACKEND="no.such.Backend"):
            resp = self.post()
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Lead.objects.count(), 1)

    def test_unsafe_next_falls_back_home(self):
        resp = self.post(next="https://evil.example.com/")
        self.assertRedirects(resp, reverse("developments:home"), fetch_redirect_response=False)

    def test_get_not_allowed(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)

    # --- spam protection ------------------------------------------------
    def assert_silently_dropped(self, resp):
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["ok"], True)  # looks like success
        self.assertFalse(Lead.objects.exists())
        self.assertEqual(len(mail.outbox), 0)

    def test_honeypot_drops_silently(self):
        self.assert_silently_dropped(self.post(ajax=True, website="http://spam.example"))

    def test_too_fast_drops_silently(self):
        self.assert_silently_dropped(self.post(ajax=True, ts=ts(seconds_ago=1)))

    def test_missing_or_forged_timestamp_drops_silently(self):
        self.assert_silently_dropped(self.post(ajax=True, ts=""))
        self.assert_silently_dropped(self.post(ajax=True, ts="1700000000:forged"))

    def test_rate_limit_per_ip(self):
        for _ in range(5):
            self.assertEqual(self.post(ajax=True).status_code, 200)
        resp = self.post(ajax=True)
        self.assertEqual(resp.status_code, 429)
        self.assertIn("try again later", resp.json()["message"])
        self.assertEqual(Lead.objects.count(), 5)


class LeadFormRenderTests(TestCase):
    def test_every_page_has_protected_form(self):
        for name in ("developments:home", "developments:contact"):
            html = self.client.get(reverse(name)).content.decode()
            self.assertIn('action="/leads/"', html)
            self.assertIn('name="csrfmiddlewaretoken"', html)
            self.assertIn('name="ts"', html)
            self.assertIn('class="lead-hp"', html)
            self.assertIn('name="next"', html)
