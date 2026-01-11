from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from main.models import Event, Student, Attendance
import random

class Command(BaseCommand):
    help = "Generate sample attendance logs for an event"

    def add_arguments(self, parser):
        parser.add_argument('event_id', type=int, help='Event ID to simulate attendance for')
        parser.add_argument('--count', type=int, default=10, help='Number of students to mark present')
        parser.add_argument('--org-only', action='store_true', help='Use only students from the event\'s organization')

    def handle(self, *args, **options):
        event_id = options['event_id']
        count = options['count']
        org_only = options['org_only']

        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            raise CommandError(f'Event {event_id} not found')

        if org_only and event.organization_id:
            students_qs = Student.objects.filter(organization_id=event.organization_id)
        else:
            students_qs = Student.objects.all()

        total_students = students_qs.count()
        if total_students == 0:
            self.stdout.write(self.style.WARNING('No students available to simulate.'))
            return

        pick_count = min(count, total_students)
        student_ids = list(students_qs.values_list('id', flat=True))
        random.shuffle(student_ids)
        selected_ids = student_ids[:pick_count]

        created = 0
        for sid in selected_ids:
            try:
                student = Student.objects.get(id=sid)
                _, was_created = Attendance.objects.get_or_create(event=event, student=student)
                if was_created:
                    created += 1
            except Student.DoesNotExist:
                continue

        self.stdout.write(self.style.SUCCESS(f'Created {created} attendance logs for event {event.id} ({event.title}).'))
