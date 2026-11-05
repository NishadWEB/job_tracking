from django.contrib.admin.views.decorators import staff_member_required
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseNotAllowed

from .forms import ApplicationForm, ApplicationUpdateForm
from .models import Application, Job


def home(request):
    return render(request, "home.html")


def job(request):
    jobs = Job.objects.all()
    return render(request, "job.html", {"jobs": jobs})


def application_create(request, id):
    job_object = get_object_or_404(Job, pk=id)

    if request.method == "POST":
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job_object
            application.save()
            return redirect("success")
    else:
        form = ApplicationForm()

    return render(
        request,
        "form.html",
        {"form": form, "job": job_object, "is_update": False},
    )


def success(request):
    return render(request, "success.html")


@staff_member_required

def application_list(request):
    applications = Application.objects.select_related("job").order_by("-applied_date", "-id")
    return render(request, "applications/list.html", {"applications": applications})


@staff_member_required

def application_detail(request, pk):
    application = get_object_or_404(Application, pk=pk)
    return render(request, "applications/detail.html", {"application": application})


@staff_member_required

def application_update(request, pk):
    application = get_object_or_404(Application, pk=pk)
    previous_resume = application.resume

    if request.method == "POST":
        form = ApplicationUpdateForm(request.POST, request.FILES, instance=application)
        if form.is_valid():
            try:
                with transaction.atomic():
                    updated_application = form.save()
            except IntegrityError:
                form.add_error("email", "An application with this email address already exists.")
            else:
                # Remove the old stored file only after the new record is saved.
                if "resume" in request.FILES and previous_resume:
                    previous_resume.storage.delete(previous_resume.name)
                return redirect("application_detail", pk=updated_application.pk)
    else:
        form = ApplicationUpdateForm(instance=application)

    return render(
        request,
        "form.html",
        {
            "form": form,
            "application": application,
            "job": application.job,
            "is_update": True,
        },
    )


@staff_member_required

def application_delete(request, pk):
    application = get_object_or_404(Application, pk=pk)

    if request.method == "POST":
        resume = application.resume
        application.delete()
        if resume:
            resume.storage.delete(resume.name)
        return redirect("application_list")

    if request.method != "GET":
        return HttpResponseNotAllowed(["GET", "POST"])

    return render(request, "applications/confirm_delete.html", {"application": application})
