from django.templatetags.static import static
from django.test import SimpleTestCase

from activity.activity.models import Activity


class ActivityImageUrlTests(SimpleTestCase):
	def test_resolved_image_url_supports_static_prefixed_paths(self):
		activity = Activity(image="static/activity/uploaded_images/example.jpg")

		self.assertEqual(
			activity.resolved_image_url,
			static("activity/uploaded_images/example.jpg"),
		)

	def test_resolved_image_url_supports_activity_relative_paths(self):
		activity = Activity(image="activity/uploaded_images/example.jpg")

		self.assertEqual(
			activity.resolved_image_url,
			static("activity/uploaded_images/example.jpg"),
		)

	def test_resolved_image_url_is_empty_without_image(self):
		activity = Activity()

		self.assertEqual(activity.resolved_image_url, "")
