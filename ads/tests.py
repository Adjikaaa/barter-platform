from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Ad, ExchangeProposal

# Тесты для модели Ad
class AdModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.ad = Ad.objects.create(
            user=self.user,
            title="Тестовое объявление",
            description="Описание товара",
            image_url="https://example.com/image.jpg ",
            category="Книги",
            condition="new"
        )

    def test_ad_creation(self):
        ad = Ad.objects.get(title="Тестовое объявление")
        self.assertEqual(ad.description, "Описание товара")
        self.assertEqual(ad.category, "Книги")
        self.assertEqual(ad.condition, "new")

    def test_ad_list_view(self):
        response = self.client.get(reverse('ad_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Тестовое объявление")


# Тесты для представлений (views)
class AdViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.other_user = User.objects.create_user(username='otheruser', password='67890')

        self.ad = Ad.objects.create(
            user=self.user,
            title="Тестовое объявление",
            description="Описание",
            category="Книги",
            condition="used"
        )

    def test_ad_detail_view(self):
        response = self.client.get(reverse('ad_detail', args=[self.ad.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Описание")

    def test_create_ad_view(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('create_ad'), {
            'title': 'Новое объявление',
            'description': 'Описание нового объявления',
            'category': 'Книги',
            'condition': 'new'
        })
        self.assertEqual(response.status_code, 302)  # Редирект после создания
        self.assertTrue(Ad.objects.filter(title='Новое объявление').exists())

    def test_edit_ad_view(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('edit_ad', args=[self.ad.pk]), {
            'title': 'Обновлённое объявление',
            'description': 'Обновлённое описание',
            'category': 'Книги',
            'condition': 'used'
        })
        self.assertEqual(response.status_code, 302)
        self.ad.refresh_from_db()
        self.assertEqual(self.ad.title, 'Обновлённое объявление')

    def test_edit_ad_by_other_user(self):
        self.client.login(username='otheruser', password='67890')
        response = self.client.get(reverse('edit_ad', args=[self.ad.pk]), follow=True)
        self.assertEqual(response.status_code, 403)

    def test_delete_ad_by_owner(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('delete_ad', args=[self.ad.pk]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Ad.objects.filter(pk=self.ad.pk).exists())

    def test_delete_ad_by_other_user(self):
        self.client.login(username='otheruser', password='67890')
        response = self.client.post(reverse('delete_ad', args=[self.ad.pk]), follow=True)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Ad.objects.filter(pk=self.ad.pk).exists())

    def test_search_ads_view(self):
        response = self.client.get(reverse('ad_list') + '?q=Тестовое&q=Описание')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Тестовое объявление")

        response = self.client.get(reverse('ad_list') + '?category=Книги')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Тестовое объявление")

        response = self.client.get(reverse('ad_list') + '?condition=new')
        self.assertEqual(response.status_code, 200)


# Тесты для предложения обмена
class ExchangeProposalTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='owner', password='12345')
        self.user2 = User.objects.create_user(username='proposer', password='67890')

        self.ad1 = Ad.objects.create(
            user=self.user1,
            title="Объявление пользователя 1",
            description="Книга",
            category="Книги",
            condition="new"
        )
        self.ad2 = Ad.objects.create(
            user=self.user2,
            title="Объявление пользователя 2",
            description="Игрушка",
            category="Игрушки",
            condition="used"
        )

    def test_send_proposal(self):
        self.client.login(username='proposer', password='67890')
        response = self.client.post(reverse('send_proposal', args=[self.ad1.pk]), {
            'comment': 'Хочу обменять'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ExchangeProposal.objects.filter(
            ad_sender=self.ad2,
            ad_receiver=self.ad1,
            comment='Хочу обменять'
        ).exists())

    def test_cannot_propose_to_own_ad(self):
        self.client.login(username='owner', password='12345')
        response = self.client.post(reverse('send_proposal', args=[self.ad1.pk]), {
            'comment': 'Попытка отправить себе'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(ExchangeProposal.objects.filter(comment='Попытка отправить себе').exists())

    def test_update_proposal_status(self):
        proposal = ExchangeProposal.objects.create(
            ad_sender=self.ad2,
            ad_receiver=self.ad1,
            status='pending',
            comment='Давайте поменяемся!'
        )
        self.client.login(username='owner', password='12345')
        response = self.client.post(reverse('update_proposal_status', args=[proposal.pk]), {
            'status': 'accepted'
        }, follow=True)
        proposal.refresh_from_db()
        self.assertEqual(proposal.status, 'accepted')

    def test_profile_view_displays_ads_and_proposals(self):
        self.client.login(username='owner', password='12345')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Мои объявления")
        self.assertContains(response, "Объявление пользователя 1")