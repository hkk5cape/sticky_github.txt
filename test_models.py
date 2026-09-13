from datetime import timedelta
from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from notes.models import Note


class NoteModelTests(TestCase):
    def test_saved_note_can_be_retrieved(self):
        note = Note.objects.create(title="Reminder", content="Prepare diagrams")
        saved = Note.objects.get(pk=note.pk)
        self.assertEqual((saved.title, saved.content), ("Reminder", "Prepare diagrams"))

    def test_string_representation_is_title(self):
        self.assertEqual(str(Note(title="Study")), "Study")

    def test_absolute_url_points_to_detail(self):
        note = Note.objects.create(title="Study", content="Tests")
        self.assertEqual(note.get_absolute_url(), reverse("notes:detail", args=[note.pk]))

    def test_timestamps_are_automatic(self):
        now = timezone.now()
        with patch("django.utils.timezone.now", return_value=now):
            note = Note.objects.create(title="Study", content="Tests")
        self.assertEqual(note.created_at, now)
        self.assertEqual(note.updated_at, now)

    def test_edit_changes_updated_time_only(self):
        start = timezone.now()
        with patch("django.utils.timezone.now", return_value=start):
            note = Note.objects.create(title="Study", content="Tests")
        with patch("django.utils.timezone.now", return_value=start + timedelta(hours=1)):
            note.content = "Revised"
            note.save()
        note.refresh_from_db()
        self.assertEqual(note.created_at, start)
        self.assertEqual(note.updated_at, start + timedelta(hours=1))

    def test_recently_edited_note_moves_to_top(self):
        start = timezone.now()
        with patch("django.utils.timezone.now", return_value=start):
            first = Note.objects.create(title="First", content="A")
        with patch("django.utils.timezone.now", return_value=start + timedelta(hours=1)):
            second = Note.objects.create(title="Second", content="B")
        self.assertEqual(list(Note.objects.all()), [second, first])
        with patch("django.utils.timezone.now", return_value=start + timedelta(hours=2)):
            first.save()
        self.assertEqual(list(Note.objects.all()), [first, second])
