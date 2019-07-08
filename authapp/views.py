from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import render, HttpResponseRedirect
from authapp.forms import ShopUserLoginForm, ShopUserEditForm, ShopUserRegisterForm
from django.contrib import auth
from django.urls import reverse
from django.conf import settings
from authapp.forms import ShopUserProfileEditForm
from authapp.models import ShopUser


def sand_verify_mail(user):
    link = reverse('auth:verify', kwargs={'email': user.email, 'activation_key': user.activation_key})
    title = 'Верификация'
    messege = 'Для удаление компьютера перейдите по ссылке {}{}' .format(settings.DOMAIN_NAME, link)
    return send_mail(title, messege, settings.EMAIL_HOST_USER, [user.email], fail_silently=False
                     )

def login(request):
    next = request.GET['next'] if 'next' in request.GET.keys() else ''
    if request.method == 'POST':
        form = ShopUserLoginForm(data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']

            user = auth.authenticate(username=username, password=password)
            if user and user.is_active:
                auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                if 'next' in request.POST.keys():
                    return HttpResponseRedirect(request.POST['next'])
                return HttpResponseRedirect(reverse('main:index'))
    else:
        form = ShopUserLoginForm()

    context = {
        'title': 'вход в систему',
        'form': form,
        'next': next,
    }
    return render(request, 'authapp/login.html', context)


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('main:index'))


def create(request):
    if request.method == 'POST':
        form = ShopUserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            user = form.save()
            if sand_verify_mail(user):
                print('Отправлено')
                return HttpResponseRedirect (reverse('auth:login'))
            return HttpResponseRedirect(reverse('auth:login'))
        else:
            print('Рабы не смогли доставить письмо')
            return HttpResponseRedirect(reverse('auth:login'))
    else:
        form = ShopUserRegisterForm()

    context = {
        'title': 'регистрация',
        'form': form
    }
    return render(request, 'authapp/register.html', context)


@transaction.atomic
def edit(request):
    title = 'редактирование'



    if request.method == 'POST':
        edit_form = ShopUserEditForm(request.POST, request.FILES, instance=request.user)
        profile_form = ShopUserProfileEditForm(request.POST, instance=request.user.shopuserprofile)
        if edit_form.is_valid() and profile_form.is_valid():
            edit_form.save()
            return HttpResponseRedirect(reverse('auth:edit'))
    else:
        edit_form = ShopUserEditForm(instance=request.user)
        profile_form = ShopUserProfileEditForm(instance=request.user.shopuserprofile)

    content = {'title': title, 'edit_form': edit_form, 'profile_form': profile_form}

    return render(request, 'authapp/edit.html', content)


def verify(request, email, activation_key):
    try:
        user = ShopUser.objectsget.get(email=email)
        if user.activation_key == activation_key and not user.is_activation_key_expired():
            print(f'user {user} is activated')
            user.is_active = True
            user.save()
            auth.login(request, user)

            return render(request, 'authapp/verification.html')
        else:
            print(f'error activation user: {user} Here')
            return render(request, 'authapp/verification.html')

    except Exception as e:
        print(f'error activation user: {e.args}')


    return HttpResponseRedirect(reverse('main'))