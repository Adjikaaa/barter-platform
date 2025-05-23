# Платформа для бартера на Django с REST API

## Установка

```bash
git clone https://github.com/yourname/barter_project.git 
cd barter_project

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python manage.py migrate
python manage.py runserver

## Тестирование
```bash
python manage.py test ads