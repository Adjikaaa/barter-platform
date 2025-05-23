from django import forms
from .models import Ad
from .models import ExchangeProposal

CATEGORIES = [
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
    ('Прочее', 'Прочее')
]

class AdForm(forms.ModelForm):
    category = forms.ChoiceField(choices=CATEGORIES)

    class Meta:
        model = Ad
        fields = ['title', 'description', 'image_url', 'category', 'condition']

class ExchangeProposalForm(forms.ModelForm):
    class Meta:
        model = ExchangeProposal
        fields = ['comment']

