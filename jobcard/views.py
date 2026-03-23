from urllib import request

from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib import messages
from .forms import TempSubmissionForm, JobCardForm, JobCardPrepopulateForm
from .models import TempSubmission, ShiftSubmission, JobCard, LINE_CHOICES, ActiveShift
from datetime import timedelta, time
import csv
from django.utils.timezone import now
from .models import ActiveShift


# -----------------------------
# Helper function (kept for fallback safety only)
# -----------------------------
def get_production_date(shift: str, current_time=None):
    now = current_time or timezone.localtime()
    today = now.date()
    if shift.lower() == "night":
        cutoff = time(5, 30)
        if now.time() < cutoff:
            return today - timedelta(days=1)
    return today

# -----------------------------
# CSV EXPORT (unchanged)
# -----------------------------
def export_jobcards_csv(request):
    start_date = request.GET.get('start_date', timezone.localdate())
    end_date = request.GET.get('end_date', timezone.localdate())
    line = request.GET.get('line')
    shift = request.GET.get('shift')

    jobcards = JobCard.objects.filter(date__range=[start_date, end_date])
    if line:
        jobcards = jobcards.filter(line=line)
    if shift:
        jobcards = jobcards.filter(shift=shift)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="jobcards_{start_date}_to_{end_date}.csv"'

    writer = csv.writer(response)
    header = [
        'Date','Line','Shift','WO Number','Product Code','Product Name','Target Quantity',
        'Hour1','Hour2','Hour3','Hour4','Hour5','Hour6','Hour7','Hour8','Hour9','Hour10','Hour11','Hour12',
        'Total Output',
        'Jar Damage','Cap Damage','Front Label Damage','Back Label Damage','Carton Damage',
        'Sleeve Damage','Sticker Damage','Tube Damage','Packets Damage','Roll On Ball Damage','Jar Pump Damage',
        'Total Damage',
        'Jar Reject','Cap Reject','Front Label Reject','Back Label Reject','Carton Reject',
        'Sleeve Reject','Sticker Reject','Tube Reject','Packets Reject','Roll On Ball Reject','Jar Pump Reject',
        'Total Reject',
        'Operators','Supervisors'
    ]
    writer.writerow(header)

    for jc in jobcards:
        row = [
            jc.date, jc.line, jc.shift, jc.wo_number, jc.product_code, jc.product_name, jc.target_quantity,
            jc.hour1, jc.hour2, jc.hour3, jc.hour4, jc.hour5, jc.hour6, jc.hour7, jc.hour8, jc.hour9, jc.hour10, jc.hour11, jc.hour12,
            jc.total_output(),
            jc.jar_damage, jc.cap_damage, jc.front_label_damage, jc.back_label_damage, jc.carton_damage,
            jc.sleeve_damage, jc.sticker_damage, jc.tube_damage, jc.packets_damage, jc.roll_on_ball_damage, jc.jar_pump_damage,
            jc.total_damage(),
            jc.jar_reject, jc.cap_reject, jc.front_label_reject, jc.back_label_reject, jc.carton_reject,
            jc.sleeve_reject, jc.sticker_reject, jc.tube_reject, jc.packets_reject, jc.roll_on_ball_reject, jc.jar_pump_reject,
            jc.total_reject(),
            jc.operator_names, jc.supervisor_names
        ]
        writer.writerow(row)

    return response

# -----------------------------
# TEMP SUBMISSION (FIXED SHIFT SOURCE ONLY)
# -----------------------------
def temp_submission(request):
    user = request.user if request.user.is_authenticated else None
    active = ActiveShift.objects.first()

    if not active:
        active = ActiveShift.objects.create(
            shift="Day",
            date=timezone.localdate()
        )

    shift = active.shift
    target_date = active.date

    selected_line = request.GET.get("line")
    lines = [l[0] for l in LINE_CHOICES]
    forms_data = []

    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        line = request.POST.get("line")
        obj, _ = TempSubmission.objects.get_or_create(
            operator=user,
            date=target_date,
            shift=shift,
            line=line
        )
        updated_fields = []
        for i in range(1, 13):
            field = f"hour{i}"
            new_val = request.POST.get(field)
            old_val = getattr(obj, field)
            if new_val in [None, ""]:
                continue
            try:
                new_val = float(new_val)
            except:
                continue
            if old_val not in [None, 0, 0.0]:
                return JsonResponse({"error": f"{field.upper()} already submitted and locked."}, status=403)
            if new_val == 0:
                continue
            setattr(obj, field, new_val)
            updated_fields.append(i)
        obj.save()
        return JsonResponse({"success": True, "updated": updated_fields})

    for line in lines:
        if selected_line and line != selected_line:
            continue
        obj, created = TempSubmission.objects.get_or_create(
            operator=user,
            date=target_date,
            shift=shift,
            line=line
        )
        if created:
            for i in range(1, 13):
                setattr(obj, f"hour{i}", 0)
            obj.save()
        form = TempSubmissionForm(instance=obj)
        forms_data.append((line, form, obj))

    return render(request, "temp_submission_form.html", {
        "forms_data": forms_data,
        "shift": shift,
        "selected_line": selected_line
    })

# -----------------------------
# SUPERVISOR DASHBOARD (unchanged)
# -----------------------------
# -----------------------------
# SUPERVISOR DASHBOARD (FIXED - STRICT ACTIVE SHIFT ONLY)
# -----------------------------
def supervisor_dashboard(request):
    active = ActiveShift.objects.first()

    if not active:
        active = ActiveShift.objects.create(
            shift="Day",
            date=timezone.localdate()
        )

    # ✅ FORCE SYSTEM SINGLE SOURCE OF TRUTH
    shift = active.shift
    target_date = active.date

    submissions = TempSubmission.objects.filter(
        date=target_date,
        shift=shift
    ).order_by("line", "operator")

    lines = [l[0] for l in LINE_CHOICES]
    global_locked_hours = []

    for h in range(1, 13):
        filled_lines = submissions.exclude(**{f"hour{h}__isnull": True}) \
                                  .exclude(**{f"hour{h}": 0}) \
                                  .values("line").distinct().count()
        if filled_lines >= len(lines):
            global_locked_hours.append(h)

    dashboard_data = {}
    for sub in submissions:
        key = f"{sub.line}_{sub.shift}"
        if key not in dashboard_data:
            dashboard_data[key] = {
                "submissions": [],
                "hour_totals": [0]*12,
                "total": 0
            }

        dashboard_data[key]["submissions"].append(sub)

        hours = [getattr(sub, f"hour{i}") or 0 for i in range(1, 13)]
        for i in range(12):
            dashboard_data[key]["hour_totals"][i] += hours[i]

        dashboard_data[key]["total"] += sum(hours)

    # AJAX response
    if request.GET.get("ajax") == "1":
        clean_data = {}
        for key, data in dashboard_data.items():
            clean_data[key] = {
                "hour_totals": data["hour_totals"],
                "total": data["total"]
            }

        return JsonResponse({
            "dashboard_data": clean_data,
            "global_locked_hours": global_locked_hours
        }, safe=True)

    return render(request, "supervisor_dashboard.html", {
        "dashboard_data": dashboard_data,
        "today": target_date,
        "hour_range": range(1, 13),
        "shift": shift
    })

# -----------------------------
# RESET SHIFT (unchanged)
# -----------------------------
def reset_shift(request):
    if request.method == "POST":
        shift = request.POST.get("shift")
        line = request.POST.get("line")

        active = ActiveShift.objects.first()

        if not active:
            active = ActiveShift.objects.create(
                shift=shift,
                date=timezone.localdate()
            )

        temp_query = TempSubmission.objects.filter(
            shift=shift,
            date=active.date
        )

        if line:
            temp_query = temp_query.filter(line=line)
            temp_query.delete()

            messages.success(
                request,
                f"✅ {shift} shift for line {line} has been reset successfully."
            )

            # ✅ LINE RESET EVENT
            active.event_type = "line_reset"
            active.line = line

        else:
            temp_query.delete()

            messages.success(
                request,
                f"✅ All lines for {shift} shift have been reset successfully."
            )

            # ✅ SHIFT RESET EVENT
            active.event_type = "shift_start"
            active.line = None

        # ✅ COMMON UPDATE (CRITICAL FIX)
        active.shift = shift
        active.last_reset = timezone.now()

        # 🔥 IMPORTANT: ensure event_type is never null
        if not active.event_type:
            active.event_type = "shift_start" if not line else "line_reset"

        active.save()

    return redirect("jobcard:supervisor_dashboard")

# -----------------------------
# FINALIZE SHIFT (unchanged)
# -----------------------------
def finalize_shift(request, line, shift):
    active = ActiveShift.objects.first()
    target_date = active.date if active else timezone.localdate()
    submissions = TempSubmission.objects.filter(
        date=target_date,
        line=line,
        shift=shift
    )
    aggregated_data = [{
        "operator": s.operator.username if s.operator else "Anonymous",
        "hours": [getattr(s, f"hour{i}") or 0 for i in range(1,13)],
        "total": s.total_output()
    } for s in submissions]
    shift_submission, created = ShiftSubmission.objects.get_or_create(
        date=target_date,
        line=line,
        shift=shift,
        defaults={"aggregated_data": aggregated_data}
    )
    if not created:
        shift_submission.aggregated_data = aggregated_data
        shift_submission.save()
    return redirect("jobcard:supervisor_dashboard")

# -----------------------------
# JOBCARD OPERATOR ENTRY (STRICT SHIFT MATCH)
# -----------------------------
def jobcard_operator_entry(request):
    active = ActiveShift.objects.first()

    if not active:
        active = ActiveShift.objects.create(
            shift="Day",
            date=timezone.localdate()
        )

    shift = active.shift
    jobcard_date = active.date
    line = request.POST.get("line") or request.GET.get("line")

    if not line:
        messages.warning(request, "Please select a Line first.")
        form = JobCardForm()
        return render(request, "jobcard_form.html", {
            "form": form,
            "shift": shift,
            "line": line
        })

    if request.method == "POST":
        wo_number = request.POST.get("wo_number")

        existing = JobCard.objects.filter(
            date=jobcard_date,
            line=line,
            shift=shift,
            wo_number=wo_number
        ).first()

        if existing:
            form = JobCardForm(request.POST, instance=existing)
        else:
            form = JobCardForm(request.POST)
            form.instance.date = jobcard_date
            form.instance.line = line
            form.instance.shift = shift

        if form.is_valid():
            jobcard = form.save(commit=False)
            jobcard.date = jobcard_date
            jobcard.line = line
            jobcard.shift = shift
            jobcard.is_submitted = True
            jobcard.save()

            if not existing:
                temp_data = TempSubmission.objects.filter(
                    date=jobcard_date,
                    line=line,
                    shift=shift
                ).first()
                if temp_data:
                    for i in range(1, 13):
                        setattr(jobcard, f"hour{i}", getattr(temp_data, f"hour{i}", 0))
                    jobcard.save()

            messages.success(request, "✅ JobCard submitted successfully!")
            return redirect("jobcard:jobcard_success")
        else:
            messages.error(request, f"Errors: {form.errors}")

    else:
        form = JobCardForm()

    return render(request, "jobcard_form.html", {
        "form": form,
        "shift": shift,
        "line": line
    })

# -----------------------------
# JOBCARD SUCCESS (unchanged)
# -----------------------------
def jobcard_success(request):
    return render(request, "success.html")

# -----------------------------
# JOBCARD PREPOPULATE (unchanged logic)
# -----------------------------
def jobcard_prepopulate(request):
    active = ActiveShift.objects.first()

    if not active:
        active = ActiveShift.objects.create(
            shift="Day",
            date=timezone.localdate()
        )

    shift = active.shift
    jobcard_date = active.date

    if request.method == "POST":
        form = JobCardPrepopulateForm(request.POST)
        if form.is_valid():
            line = form.cleaned_data['line']
            wo_number = form.cleaned_data.get('wo_number')

            jobcard, created = JobCard.objects.get_or_create(
                date=jobcard_date,
                line=line,
                shift=shift,
                wo_number=wo_number,
                defaults=form.cleaned_data
            )

            if not created:
                for field, value in form.cleaned_data.items():
                    if field not in ['line', 'wo_number']:
                        setattr(jobcard, field, value)
                jobcard.save()
                messages.success(request, f"JobCard for {line} WO {wo_number} ({shift}) updated.")
            else:
                messages.success(request, f"JobCard for {line} WO {wo_number} ({shift}) created.")

            return redirect('jobcard:jobcard_prepopulate')
    else:
        form = JobCardPrepopulateForm()

    return render(request, "jobcard_prepopulate.html", {"form": form})

# -----------------------------
# GET JOBCARD AJAX (STRICT SHIFT MATCH)
# -----------------------------
def get_jobcard(request):
    line = request.GET.get("line")
    active = ActiveShift.objects.first()

    if not active:
        return JsonResponse({"error": "No active shift set. Please wait for supervisor to start a shift."})

    shift = active.shift
    target_date = active.date

    job = JobCard.objects.filter(
        line=line,
        shift=shift,
        date=target_date
    ).order_by('-id').first()

    if not job:
        return JsonResponse({"error": "No JobCard found for this line & shift."})

    temp = TempSubmission.objects.filter(
        date=target_date,
        line=line,
        shift=shift
    ).first()

    hours = []
    for i in range(1, 13):
        if temp and getattr(temp, f"hour{i}", None) is not None:
            hours.append(getattr(temp, f"hour{i}"))
        else:
            hours.append(getattr(job, f"hour{i}", 0))

    return JsonResponse({
        "wo_number": job.wo_number,
        "product_code": job.product_code,
        "product_name": job.product_name,
        "target_quantity": job.target_quantity,
        "operator_names": job.operator_names,
        "supervisor_names": job.supervisor_names,
        "hours": hours,
        "submitted": bool(job.is_submitted)
    })

# -----------------------------
# CSRF FAILURE (unchanged)
# -----------------------------
def custom_csrf_failure(request, reason=""):
    return render(request, "csrf_failure.html", status=403)

# One more view to provide active shift info for frontend
def get_active_shift(request):
    active = ActiveShift.objects.first()

    if not active:
        return JsonResponse({"error": "No active shift"})

    return JsonResponse({
        "shift": active.shift,
        "date": str(active.date),
        "last_reset": str(active.last_reset) if active.last_reset else None,
        "line": getattr(active, "line", None),
        "event_type": getattr(active, "event_type", None),
    })


# ACTIVE SHIFT SETTER (for supervisor to change shift)
def set_active_shift(request):
    if request.method == "POST":
        shift = request.POST.get("shift")

        active = ActiveShift.objects.first()
        if not active:
            active = ActiveShift.objects.create(
                shift=shift,
                date=timezone.localdate()
            )
        else:
            active.shift = shift
            active.save()

    return redirect("jobcard:supervisor_dashboard")