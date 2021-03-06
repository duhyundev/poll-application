import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question, Choice


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


def create_choice(question_id, choice_text):
    selected_question = Question.objects.get(id=question_id)
    return selected_question.choice_set.create(choice_text='choice_text')


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        # When
        response = self.client.get(reverse('polls:index'))

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_question_with_no_choice(self):
        # Given
        create_question(
            question_text="Past question with no Choice.", days=-30)

        # When
        response = self.client.get(reverse('polls:index'))

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        # Given
        created_question = create_question(
            question_text="Past question.", days=-30)
        create_choice(created_question.id, 'choice of Past question.')

        # When
        response = self.client.get(reverse('polls:index'))

        # Assert
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_future_question(self):
        # Given
        created_question = create_question(
            question_text="Future question.", days=30)
        create_choice(created_question.id, 'choice of Future question.')

        # When
        response = self.client.get(reverse('polls:index'))

        # Assert
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(
            response.context['latest_question_list'], []
        )

    def test_future_question_and_past_question(self):
        # Given
        created_question1 = create_question(
            question_text="Past question.", days=-30)
        create_choice(created_question1.id, 'choice of Past question.')

        created_question2 = create_question(
            question_text="Future question.", days=30)
        create_choice(created_question2.id, 'choice of Future question.')

        # When
        response = self.client.get(reverse('polls:index'))

        # Assert
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_two_past_questions(self):
        # Given
        created_question1 = create_question(
            question_text="Past question 1.", days=-30)
        create_choice(created_question1.id, 'choice of Past question 1.')

        created_question2 = create_question(
            question_text='Past question 2.', days=-5)
        create_choice(created_question2.id, 'choice of Past question 2.')

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


class QuestionResultsView(TestCase):
    def test_past_question_with_choice(self):
        # Given
        past_question_with_choice = create_question(
            question_text='I have Choice.', days=-1)
        create_choice(past_question_with_choice.id, 'choice 1.')

        url = reverse('polls:results', args=(
            past_question_with_choice.id,))
        # When
        response = self.client.get(url)

        # Assert
        self.assertContains(
            response, past_question_with_choice.question_text)

    def test_past_question_with_no_choice(self):
        # Given
        past_question_with_no_choice = create_question(
            question_text='I have no Choice.', days=-1)

        url = reverse('polls:results', args=(
            past_question_with_no_choice.id,))

        # When
        response = self.client.get(url)

        # Assert
        self.assertEqual(response.status_code, 404)
