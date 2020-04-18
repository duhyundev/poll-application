import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        # Given
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)

        # Assert
        self.assertIs(
            future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_questions(self):
        # Given
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)

        # Assert
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_with_recently_question(self):
        # Given
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)

        # Assert
        self.assertIs(recent_question.was_published_recently(), True)


# Helper
def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        # When
        response = self.client.get(reverse('polls:index'))

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        # Given
        create_question(question_text="Past question.", days=-30)

        # When
        response = self.client.get(reverse('polls:index'))

        # Assert
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_future_question(self):
        # Given
        create_question(question_text="Future question.", days=30)

        # When
        response = self.client.get(reverse('polls:index'))

        # Assert
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(
            response.context['latest_question_list'], []
        )

    def test_future_question_and_past_question(self):
        # Given
        create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)

        # When
        response = self.client.get(reverse('polls:index'))

        # Assert
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_two_past_questions(self):
        # Given
        create_question(question_text="Past question 1.", days=-30)
        create_question(question_text='Past question 2.', days=-5)

        # When
        response = self.client.get(reverse('polls:index'))

        # Assert
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )


class QuestionDetailView(TestCase):
    def test_future_question(self):
        # Given
        future_question = create_question(
            question_text='Future question.', days=5)
        url = reverse('polls:detail', args=(future_question.id,))

        # When
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        # Given
        past_question = create_question(
            question_text='Past Question.', days=-5)
        url = reverse('polls:detail', args=(past_question.id,))

        # When
        response = self.client.get(url)

        # Assert
        self.assertContains(response, past_question.question_text)


""" We ought to add a similar get_queryset method to ResultsView and create a new test class for that view. 
It’ll be very similar to what we have just created; in fact there will be a lot of repetition.

We could also improve our application in other ways, adding tests along the way. 
For example, it’s silly that Questions can be published on the site that have no Choices. 
So, our views could check for this, and exclude such Questions. 

Our tests would create a Question without Choices and then test that it’s not published, as well as create a similar Question with Choices, and test that it is published.

Perhaps logged-in admin users should be allowed to see unpublished Questions, but not ordinary visitors. 
Again: whatever needs to be added to the software to accomplish this should be accompanied by a test, 
whether you write the test first and then make the code pass the test, or work out the logic in your code first and then write a test to prove it.

At a certain point you are bound to look at your tests and wonder whether your code is suffering from test bloat, which brings us to: """


class QuestionResultsView(TestCase):
    def test_question_with_no_choice(self):
        # Given

        # When

        # Assert
