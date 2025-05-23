from django.db import models
from django.contrib.auth.models import User

CATEGORY_CHOICES = [
    ('Одежда', 'Одежда'),
    ('Обувь', 'Обувь'),
    ('Аксессуары', 'Аксессуары'),
    ('Бижутерия', 'Бижутерия'),
    ('Книги', 'Книги'),
    ('Игрушки', 'Игрушки'),
    ('Мебель', 'Мебель'),
    ('Бытовая техника', 'Бытовая техника'),
    ('Товары для ремонта', 'Товары для ремонта'),
    ('Садовые инструменты', 'Садовые инструменты'),
    ('Компьютеры', 'Компьютеры'),
    ('Телефоны', 'Телефоны'),
    ('Планшеты', 'Планшеты'),
    ('Аудио и видеотехника', 'Аудио и видеотехника'),
    ('Товары для спорта', 'Товары для спорта'),
    ('Путешествия', 'Путешествия'),
    ('Творчество', 'Творчество'),
    ('Прочее', 'Прочее'),
]

from django.db import models
from django.contrib.auth.models import User

class Ad(models.Model):
    CONDITION_CHOICES = [
        ('new', 'Новый'),
        ('used', 'Б/у')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField('Наименование', max_length=255)
    description = models.TextField('Описание')
    image_url = models.URLField('URL изображения', blank=True, null=True)
    category = models.CharField('Категория', max_length=100)
    condition = models.CharField('Состояние', max_length=10, choices=CONDITION_CHOICES)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    def __str__(self):
        return self.title

class ExchangeProposal(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('accepted', 'Принята'),
        ('rejected', 'Отклонена')
    ]

    ad_sender = models.ForeignKey(Ad, related_name='sent_proposals', on_delete=models.CASCADE)
    ad_receiver = models.ForeignKey(Ad, related_name='received_proposals', on_delete=models.CASCADE)
    comment = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Предложение от {self.ad_sender} к {self.ad_receiver}"
