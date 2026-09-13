from django.test import TestCase
from notes.forms import NoteForm
from notes.models import Note


class NoteFormTests(TestCase):
    def test_valid_form_saves_unicode_and_multiline_text(self):
        form = NoteForm(data={"title": "Idées ✨", "content": "First line\nDeuxième ligne"})
        self.assertTrue(form.is_valid(), form.errors)
        note = form.save()
        note.refresh_from_db()
        self.assertEqual(note.title, "Idées ✨")
        self.assertEqual(note.content, "First line\nDeuxième ligne")

    def test_title_at_limit_is_valid(self):
        form = NoteForm(data={"title": "A" * 200, "content": "Body"})
        self.assertTrue(form.is_valid(), form.errors)

    def test_each_field_is_required(self):
        for field in ("title", "content"):
            with self.subTest(field=field):
                data = {"title": "Title", "content": "Body"}
                del data[field]
                form = NoteForm(data=data)
                self.assertFalse(form.is_valid())
                self.assertIn(field, form.errors)

    def test_whitespace_only_fields_are_invalid(self):
        form = NoteForm(data={"title": " ", "content": " \n "})
        self.assertFalse(form.is_valid())
        self.assertEqual(set(form.errors), {"title", "content"})

    def test_outer_whitespace_is_trimmed(self):
        form = NoteForm(data={"title": "  Reminder  ", "content": "  Call tomorrow  "})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data, {"title": "Reminder", "content": "Call tomorrow"})

    def test_edit_updates_existing_row(self):
        note = Note.objects.create(title="Old", content="Old body")
        form = NoteForm(data={"title": "New", "content": "New body"}, instance=note)
        self.assertTrue(form.is_valid())
        saved = form.save()
        self.assertEqual(saved.pk, note.pk)
        self.assertEqual(Note.objects.count(), 1)
        note.refresh_from_db()
        self.assertEqual(note.title, "New")

    def test_extra_fields_cannot_override_identity_or_creation_date(self):
        note = Note.objects.create(title="Old", content="Old body")
        created = note.created_at
        original_pk = note.pk
        form = NoteForm(data={"title": "New", "content": "Body", "id": 999, "created_at": "2000-01-01"}, instance=note)
        self.assertTrue(form.is_valid())
        form.save()
        note.refresh_from_db()
        self.assertEqual(note.pk, original_pk)
        self.assertEqual(note.created_at, created)
