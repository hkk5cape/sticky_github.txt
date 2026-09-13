from django.test import Client, TestCase
from django.urls import reverse
from notes.models import Note


class NoteWorkflowTests(TestCase):
    def setUp(self):
        self.note = Note.objects.create(title="Shopping", content="Milk and bread")

    def test_list_and_detail(self):
        self.assertContains(self.client.get(reverse("notes:list")), "Shopping")
        self.assertContains(self.client.get(self.note.get_absolute_url()), "Milk and bread")

    def test_empty_board(self):
        Note.objects.all().delete()
        self.assertContains(self.client.get(reverse("notes:list")), "A fresh page awaits")

    def test_create(self):
        response = self.client.post(reverse("notes:create"), {"title": "Study", "content": "Django"})
        note = Note.objects.get(title="Study")
        self.assertRedirects(response, note.get_absolute_url())

    def test_blank_input_rejected(self):
        response = self.client.post(reverse("notes:create"), {"title": "  ", "content": ""})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Note.objects.count(), 1)
        self.assertIn("title", response.context["form"].errors)
        self.assertIn("content", response.context["form"].errors)

    def test_long_title_rejected(self):
        response = self.client.post(reverse("notes:create"), {"title": "x" * 201, "content": "Body"})
        self.assertIn("title", response.context["form"].errors)
        self.assertEqual(Note.objects.count(), 1)

    def test_edit(self):
        response = self.client.post(reverse("notes:update", args=[self.note.pk]), {"title": "Updated", "content": "New text"})
        self.assertRedirects(response, self.note.get_absolute_url())
        self.note.refresh_from_db()
        self.assertEqual(self.note.content, "New text")
        self.assertEqual(self.note.title, "Updated")

    def test_invalid_edit_preserves_note(self):
        self.client.post(reverse("notes:update", args=[self.note.pk]), {"title": "", "content": ""})
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, "Shopping")

    def test_delete_requires_post(self):
        url = reverse("notes:delete", args=[self.note.pk])
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertTrue(Note.objects.filter(pk=self.note.pk).exists())
        self.assertRedirects(self.client.post(url), reverse("notes:list"))
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())

    def test_missing_notes_return_404(self):
        for view in ("detail", "update", "delete"):
            self.assertEqual(self.client.get(reverse("notes:" + view, args=[9999])).status_code, 404)

    def test_html_is_escaped(self):
        self.note.content = "<script>alert(1)</script>"
        self.note.save()
        response = self.client.get(self.note.get_absolute_url())
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, "<script>")

    def test_csrf_protection(self):
        client = Client(enforce_csrf_checks=True)
        for url in (reverse("notes:create"), reverse("notes:update", args=[self.note.pk]), reverse("notes:delete", args=[self.note.pk])):
            self.assertEqual(client.post(url, {"title": "Test", "content": "Body"}).status_code, 403)

    def test_pagination(self):
        Note.objects.bulk_create([Note(title=f"Note {i}", content="Body") for i in range(12)])
        response = self.client.get(reverse("notes:list"))
        self.assertEqual(len(response.context["notes"]), 12)
        self.assertTrue(response.context["is_paginated"])


class NoteInteractionTests(TestCase):
    def setUp(self):
        self.note = Note.objects.create(title="Plan", content="First line\nSecond line")

    def test_create_form_loads_without_saving(self):
        response = self.client.get(reverse("notes:create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "notes/note_form.html")
        self.assertEqual(Note.objects.count(), 1)

    def test_edit_form_is_prefilled(self):
        response = self.client.get(reverse("notes:update", args=[self.note.pk]))
        self.assertEqual(response.context["form"].initial["title"], "Plan")
        self.assertEqual(response.context["form"].initial["content"], self.note.content)

    def test_cancel_edit_returns_to_unchanged_note(self):
        response = self.client.get(reverse("notes:update", args=[self.note.pk]))
        self.assertContains(response, f'href="{self.note.get_absolute_url()}">Cancel</a>')
        self.client.get(self.note.get_absolute_url())
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, "Plan")

    def test_cancel_delete_keeps_note(self):
        response = self.client.get(reverse("notes:delete", args=[self.note.pk]))
        self.assertContains(response, f'href="{self.note.get_absolute_url()}">Keep note</a>')
        self.assertEqual(self.client.get(self.note.get_absolute_url()).status_code, 200)
        self.assertTrue(Note.objects.filter(pk=self.note.pk).exists())

    def test_success_messages_after_mutations(self):
        response = self.client.post(reverse("notes:create"), {"title": "New", "content": "Body"}, follow=True)
        self.assertContains(response, "Note created.")
        response = self.client.post(reverse("notes:update", args=[self.note.pk]), {"title": "Updated", "content": "Body"}, follow=True)
        self.assertContains(response, "Note updated.")
        response = self.client.post(reverse("notes:delete", args=[self.note.pk]), follow=True)
        self.assertContains(response, "Note deleted.")

    def test_delete_affects_only_selected_note(self):
        other = Note.objects.create(title="Keep", content="Body")
        self.client.post(reverse("notes:delete", args=[self.note.pk]))
        self.assertEqual(list(Note.objects.values_list("pk", flat=True)), [other.pk])

    def test_second_page_contains_remaining_note(self):
        Note.objects.bulk_create([Note(title=f"Item {i}", content="Body") for i in range(12)])
        first = self.client.get(reverse("notes:list"))
        second = self.client.get(reverse("notes:list"), {"page": 2})
        self.assertEqual(len(second.context["notes"]), 1)
        self.assertTrue(set(first.context["notes"]).isdisjoint(second.context["notes"]))

    def test_invalid_page_returns_404(self):
        for page in ("abc", "0", "99"):
            with self.subTest(page=page):
                self.assertEqual(self.client.get(reverse("notes:list"), {"page": page}).status_code, 404)

    def test_multiline_content_retains_line_breaks(self):
        self.assertContains(self.client.get(self.note.get_absolute_url()), "First line<br>Second line", html=False)

    def test_csrf_token_allows_normal_form_submission(self):
        client = Client(enforce_csrf_checks=True)
        client.get(reverse("notes:create"))
        token = client.cookies["csrftoken"].value
        response = client.post(reverse("notes:create"), {"title": "CSRF checked", "content": "Body", "csrfmiddlewaretoken": token})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Note.objects.filter(title="CSRF checked").exists())
