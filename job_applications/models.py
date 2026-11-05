from django.db import models
from django.utils import timezone

class Job(models.Model):
    title = models.CharField(max_length=50)
    desc = models.CharField(max_length=250)
    dept = models.CharField(max_length=20)
    location = models.CharField(max_length=50)
    job_type = models.CharField(max_length=50)

    class Meta: 
        db_table = 'jobs'
        ordering = ['id']

class Application(models.Model):
    STATUS = [
        ('APPLIED', 'Applied'),
        ('UNDER_REVIEW', 'Under Review'),
        ('SHORTLISTED', 'Shortlisted'),
        ('SELECTED', 'Selected'),
        ('REJECTED', 'Rejected'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=14)
    resume = models.FileField(upload_to='resumes/')

    # Below two fields are hidden in forms(HR use only)
    status = models.CharField(max_length=20, choices=STATUS, default='APPLIED')
    applied_date = models.DateField(default=timezone.now)

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='applications'
    )

    class Meta:
        db_table = 'applications'
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(
                fields=['email'],
                name='unique_employee_email'
            )
        ]