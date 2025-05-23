from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseForbidden
from django.db.models import Q
from rest_framework import viewsets, permissions
from .models import Ad, ExchangeProposal
from .forms import AdForm, ExchangeProposalForm
from .serializers import AdSerializer, ExchangeProposalSerializer

def index(request):
	return render(request, "ads/index.html")

@login_required
def create_ad(request):
    if request.method == 'POST':
        form = AdForm(request.POST)
        if form.is_valid():
            ad = form.save(commit=False)
            ad.user = request.user
            ad.save()
            return redirect('ad_list')
    else:
        form = AdForm()

    return render(request, 'ads/ad_form.html', {'form': form, 'title': 'Создать объявление'})

def ad_detail(request, pk):
    ad = get_object_or_404(Ad, pk=pk)
    return render(request, 'ads/ad_detail.html', {'ad': ad})

@login_required
def edit_ad(request, pk):
    ad = get_object_or_404(Ad, pk=pk)
    if ad.user != request.user:
        return HttpResponseForbidden("Вы не можете редактировать это объявление.")
    if request.method == 'POST':
        form = AdForm(request.POST, instance=ad)
        if form.is_valid():
            form.save()
            return redirect('ad_list')
    else:
        form = AdForm(instance=ad)
    return render(request, 'ads/ad_form.html', {'form': form})


@login_required
def delete_ad(request, pk):
    ad = get_object_or_404(Ad, pk=pk)

    if ad.user != request.user:
        return HttpResponseForbidden("Вы не можете удалить это объявление.")

    if request.method == 'POST':
        ad.delete()
        return redirect('ad_list')

    return render(request, 'ads/ad_confirm_delete.html', {'ad': ad})


def search_ads(request):
    CATEGORIES = [
        'Одежда', 'Обувь', 'Аксессуары', 'Бижутерия',
        'Книги', 'Игрушки', 'Мебель', 'Бытовая техника',
        'Товары для ремонта', 'Садовые инструменты',
        'Компьютеры', 'Телефоны', 'Планшеты',
        'Аудио и видеотехника',
        'Товары для спорта', 'Путешествия', 'Творчество', 'Прочее'
    ]

    query = request.GET.get('q')
    category = request.GET.get('category')
    condition = request.GET.get('condition')

    ads = Ad.objects.all()

    if query:
        ads = ads.filter(title__icontains=query) | ads.filter(description__icontains=query)
    if category:
        ads = ads.filter(category=category)
    if condition:
        ads = ads.filter(condition=condition)

    paginator = Paginator(ads, 10)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'ads/ad_list.html', {
        'page_obj': page_obj,
        'categories': CATEGORIES,
        'current_category': category,
        'current_condition': condition,
        'current_query': query,
    })


@login_required
def send_proposal(request, pk):
    ad_receiver = get_object_or_404(Ad, pk=pk)

    if ad_receiver.user == request.user:
        messages.error(request, "Нельзя предложить обмен на собственное объявление.")
        return redirect('ad_detail', pk=pk)

    if request.method == 'POST':
        form = ExchangeProposalForm(request.POST)
        if form.is_valid():
            user_ads = Ad.objects.filter(user=request.user)
            if not user_ads.exists():
                messages.error(request, "У вас нет объявлений для предложения обмена.")
                return redirect('ad_detail', pk=pk)

            ad_sender = user_ads.first()

            proposal = form.save(commit=False)
            proposal.ad_sender = ad_sender
            proposal.ad_receiver = ad_receiver
            proposal.status = 'pending'
            proposal.save()
            messages.success(request, "Ваше предложение обмена отправлено!")
            return redirect('ad_detail', pk=pk)
    else:
        form = ExchangeProposalForm()

    return render(request, 'ads/send_proposal.html', {'form': form, 'ad': ad_receiver})

@login_required
def exchange_proposals_list(request):
    """Список всех предложений, связанных с пользователем"""
    proposals = ExchangeProposal.objects.filter(
        Q(ad_sender__user=request.user) |
        Q(ad_receiver__user=request.user)).distinct().order_by('-created_at')

    return render(request, 'ads/proposal_list.html', {'proposals': proposals})

@login_required
def proposal_detail(request, pk):
    """Детали конкретного предложения"""
    proposal = get_object_or_404(ExchangeProposal, pk=pk)

    if request.user not in [proposal.ad_sender.user, proposal.ad_receiver.user]:
        messages.error(request, "Доступ запрещён.")
        return redirect('ad_list')

    return render(request, 'ads/proposal_detail.html', {'proposal': proposal})


@login_required
def update_exchange_proposal_status(request, pk):
    """Обновление статуса предложения обмена (только получатель может принять/отклонить)"""
    proposal = get_object_or_404(ExchangeProposal, pk=pk)

    if proposal.ad_receiver.user != request.user:
        messages.error(request, "Вы не можете изменить статус этого предложения.")
        return redirect('proposal_detail', pk=pk)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(ExchangeProposal.STATUS_CHOICES).keys():
            proposal.status = new_status
            proposal.save()
            messages.success(request, f"Статус предложения изменён на '{dict(ExchangeProposal.STATUS_CHOICES)[proposal.status]}'.")
        else:
            messages.error(request, "Некорректный статус.")

    return redirect('proposal_detail', pk=pk)

# REST API ViewSets
class AdViewSet(viewsets.ModelViewSet):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ExchangeProposalViewSet(viewsets.ModelViewSet):
    queryset = ExchangeProposal.objects.all()
    serializer_class = ExchangeProposalSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
