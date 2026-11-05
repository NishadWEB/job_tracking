import shutil
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .forms import ApplicationForm
from .models import Application, Job


TEST_MEDIA_ROOT = Path(settings.BASE_DIR) / "test_media"


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class ApplicationFormTests(TestCase):
    def tearDown(self):
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)

    def test_phone_must_be_valid(self):
        form = ApplicationForm(
            data={"name": "Test Applicant", "email": "test@example.com", "phone": "abc12345"},
            files={"resume": SimpleUploadedFile("resume.pdf", b"PDF content")},
        )
        self.assertFalse(form.is_valid())
        self.assertIn("phone", form.errors)

    def test_resume_must_have_an_allowed_extension(self):
        form = ApplicationForm(
            data={"name": "Test Applicant", "email": "test@example.com", "phone": "9876543210"},
            files={"resume": SimpleUploadedFile("resume.txt", b"Not a resume PDF")},
        )
        self.assertFalse(form.is_valid())
        self.assertIn("resume", form.errors)

    def test_resume_must_not_exceed_five_mb(self):
        large_file = SimpleUploadedFile("resume.pdf", b"x" * (5 * 1024 * 1024 + 1))
        form = ApplicationForm(
            data={"name": "Test Applicant", "email": "test@example.com", "phone": "9876543210"},
            files={"resume": large_file},
        )
        self.assertFalse(form.is_valid())
        self.assertIn("resume", form.errors)


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class ApplicationCRUDTests(TestCase):
    def setUp(self):
        self.job = Job.objects.create(
            title="Python Developer",
            desc="Build and maintain backend services.",
            dept="Engineering",
            location="Bengaluru",
            job_type="Full Time",
        )
        self.hr_user = get_user_model().objects.create_user(
            username="hr-user",
            password="test-password",
            is_staff=True,
        )

    def tearDown(self):
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)

    @staticmethod
    def uploaded_resume(name="resume.pdf"):
        return SimpleUploadedFile(name, b"%PDF-1.4 test resume content", content_type="application/pdf")

    def create_application(self, email="applicant@example.com"):
        return Application.objects.create(
            name="Test Applicant",
            email=email,
            phone="9876543210",
            resume=self.uploaded_resume(),
            job=self.job,
        )

    def login_as_hr(self):
        self.client.force_login(self.hr_user)

    def test_applicant_can_submit_application_with_modelform(self):
        response = self.client.post(
            reverse("application_form", args=[self.job.pk]),
            {
                "name": "New Applicant",
                "email": "new@example.com",
                "phone": "+91 9876543210",
                "resume": self.uploaded_resume(),
            },
        )

        self.assertRedirects(response, reverse("success"))
        application = Application.objects.get(email="new@example.com")
        self.assertEqual(application.job, self.job)
        self.assertTrue(application.resume.name.endswith(".pdf"))

    def test_invalid_application_is_not_saved(self):
        response = self.client.post(
            reverse("application_form", args=[self.job.pk]),
            {
                "name": "New Applicant",
                "email": "new@example.com",
                "phone": "not-a-phone",
                "resume": self.uploaded_resume(),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enter a valid phone number")
        self.assertEqual(Application.objects.count(), 0)


    def test_duplicate_email_is_rejected(self):
        self.create_application(email="duplicate@example.com")

        response = self.client.post(
            reverse("application_form", args=[self.job.pk]),
            {
                "name": "Another Applicant",
                "email": "duplicate@example.com",
                "phone": "9876543210",
                "resume": self.uploaded_resume("another-resume.pdf"),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Application.objects.filter(email="duplicate@example.com").count(), 1)

    def test_staff_can_read_application_list_and_detail(self):
        application = self.create_application()
        self.login_as_hr()

        list_response = self.client.get(reverse("application_list"))
        detail_response = self.client.get(reverse("application_detail", args=[application.pk]))

        self.assertEqual(list_response.status_code, 200)
        self.assertContains(list_response, "Test Applicant")
        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(detail_response, "applicant@example.com")

    def test_non_staff_cannot_read_application_list(self):
        response = self.client.get(reverse("application_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response.url)

    def test_staff_can_update_application_and_keep_existing_resume(self):
        application = self.create_application()
        original_resume_name = application.resume.name
        self.login_as_hr()

        response = self.client.post(
            reverse("application_update", args=[application.pk]),
            {
                "name": "Updated Applicant",
                "email": "applicant@example.com",
                "phone": "9876543211",
                "status": "SHORTLISTED",
            },
        )

        self.assertRedirects(response, reverse("application_detail", args=[application.pk]))
        application.refresh_from_db()
        self.assertEqual(application.name, "Updated Applicant")
        self.assertEqual(application.status, "SHORTLISTED")
        self.assertEqual(application.resume.name, original_resume_name)


    def test_staff_can_replace_resume(self):
        application = self.create_application()
        old_resume_path = Path(application.resume.path)
        self.login_as_hr()

        response = self.client.post(
            reverse("application_update", args=[application.pk]),
            {
                "name": application.name,
                "email": application.email,
                "phone": application.phone,
                "status": application.status,
                "resume": self.uploaded_resume("updated-resume.pdf"),
            },
        )

        self.assertRedirects(response, reverse("application_detail", args=[application.pk]))
        application.refresh_from_db()
        self.assertTrue(application.resume.name.endswith("updated-resume.pdf"))
        self.assertFalse(old_resume_path.exists())

    def test_staff_can_delete_application_after_confirmation(self):
        application = self.create_application()
        resume_path = Path(application.resume.path)
        self.login_as_hr()

        confirm_response = self.client.get(reverse("application_delete", args=[application.pk]))
        self.assertEqual(confirm_response.status_code, 200)

        delete_response = self.client.post(reverse("application_delete", args=[application.pk]))
        self.assertRedirects(delete_response, reverse("application_list"))
        self.assertFalse(Application.objects.filter(pk=application.pk).exists())
        self.assertFalse(resume_path.exists())
