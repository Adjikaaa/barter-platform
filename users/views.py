from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ads.models import Ad, ExchangeProposal
from .forms import UserRegisterForm

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Ваш аккаунт, {username}, создан: можно войти на сайт.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    user = request.user

    user_ads = Ad.objects.filter(user=user).prefetch_related('received_proposals', 'sent_proposals')
    received_proposals = ExchangeProposal.objects.filter(ad_receiver__user=user).select_related('ad_sender')
    sent_proposals = ExchangeProposal.objects.filter(ad_sender__user=user).select_related('ad_receiver')

    return render(request, 'users/profile.html', {
        'user': user,
        'user_ads': user_ads,
        'received_proposals': received_proposals,
        'sent_proposals': sent_proposals
    })

@login_required
def logout_view(request):
    logout(request)
    return redirect('logout_success')