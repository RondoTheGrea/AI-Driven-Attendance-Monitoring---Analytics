from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.conf import settings
import json
from main.models import Student, Event, Attendance, Organization

def home(request):
    return render(request, 'main/index.html')

def org_login(request):
    return render(request, 'main/org-page.html')

def student_login(request):
    return render(request, 'main/student-page.html')


@csrf_exempt
def rfid_scan(request):
    """Receive RFID scans from a reader device and record attendance.

    Expected POST payload (JSON or form):
    - rfid_uid: string (student's RFID UID)
    - event_id: integer (target event ID) [optional]

    Auth: provide shared token in header `X-Reader-Token` matching settings.RFID_READER_TOKEN.
    """
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'POST required'}, status=405)

    # Simple shared secret auth
    token = request.headers.get('X-Reader-Token') or request.META.get('HTTP_X_READER_TOKEN')
    if not token:
        return JsonResponse({'ok': False, 'error': 'unauthorized'}, status=401)

    # Prefer org-level reader token, fallback to global dev token
    org = Organization.objects.filter(reader_token=token).first()
    global_ok = getattr(settings, 'RFID_READER_TOKEN', None) and token == settings.RFID_READER_TOKEN
    if not org and not global_ok:
        return JsonResponse({'ok': False, 'error': 'unauthorized'}, status=401)

    # Parse body (support JSON or form-encoded)
    rfid_uid = None
    event_id = None
    try:
        if request.content_type and 'application/json' in request.content_type:
            data = json.loads(request.body.decode('utf-8'))
            rfid_uid = (data.get('rfid_uid') or '').strip()
            event_id = data.get('event_id')
        else:
            rfid_uid = (request.POST.get('rfid_uid') or '').strip()
            event_id = request.POST.get('event_id')
            event_id = int(event_id) if event_id else None
    except Exception:
        return JsonResponse({'ok': False, 'error': 'invalid_payload'}, status=400)

    if not rfid_uid:
        return JsonResponse({'ok': False, 'error': 'rfid_uid_required'}, status=400)

    # Resolve student by RFID
    try:
        student = Student.objects.get(rfid_uid=rfid_uid)
    except Student.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'student_not_found'}, status=404)

    now = timezone.now()

    # Resolve target event
    event = None
    if event_id:
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return JsonResponse({'ok': False, 'error': 'event_not_found'}, status=404)
        # If org token provided, ensure event belongs to that org
        if org and event.organization_id != org.id:
            return JsonResponse({'ok': False, 'error': 'event_wrong_org'}, status=403)
    else:
        # Fallback: find an active ongoing event
        candidates = Event.objects.filter(is_active=True)
        if org:
            candidates = candidates.filter(organization_id=org.id)
        for e in candidates:
            start_dt = timezone.make_aware(timezone.datetime.combine(e.event_date, e.start_time)) if timezone.is_naive(timezone.datetime.combine(e.event_date, e.start_time)) else timezone.datetime.combine(e.event_date, e.start_time)
            end_dt = timezone.make_aware(timezone.datetime.combine(e.event_date, e.end_time)) if timezone.is_naive(timezone.datetime.combine(e.event_date, e.end_time)) else timezone.datetime.combine(e.event_date, e.end_time)
            if start_dt <= now <= end_dt:
                event = e
                break
        if event is None:
            return JsonResponse({'ok': False, 'error': 'no_active_event'}, status=400)

    # Optional: ensure student and event share organization if defined
    if student.organization and event.organization and student.organization_id != event.organization_id:
        return JsonResponse({'ok': False, 'error': 'org_mismatch'}, status=403)

    # Create attendance log (idempotent via unique_together)
    att, created = Attendance.objects.get_or_create(event=event, student=student)

    return JsonResponse({
        'ok': True,
        'created': created,
        'event': {
            'id': event.id,
            'title': event.title,
        },
        'student': {
            'id': student.id,
            'student_id': student.student_id,
        },
    }, status=200)
