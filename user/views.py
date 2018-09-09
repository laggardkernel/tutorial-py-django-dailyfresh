from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse, HttpResponseRedirect

from .models import User, Contact


def register(request):
    if request.method == 'POST':
        username = request.POST.get('user_name')
        password1 = request.POST.get('pwd')
        password2 = request.POST.get('cpwd')
        email = request.POST.get('email')

        if password1 != password2:
            return redirect(reverse('user:register'))

        user = User(username=username, password=password1, email=email)
        user.save()

        return redirect(reverse('user:login'))
    context = {'title': '用户注册'}
    return render(request, 'user/register.html')


def register_check(request):
    username = request.GET.get('username', None)
    count = User.objects.filter(username=username).count()
    return JsonResponse({'count': count})


def login(request):
    error = 0

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        remember = request.POST.get('remember', 0)

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            error = 1
            user = None

        if user:
            if user.verify_password(password):
                resp = HttpResponseRedirect(reverse('user:info'))
                if remember != 0:
                    resp.set_cookie('username', user.username)
                else:
                    resp.set_cookie('username', '', max_age=-1)
                # 减小页面显示时相关查询
                request.session['user_id'] = user.id
                request.session['user_name'] = user.username
                return resp
            else:
                error = 1

        context = {'title': '用户登录', 'error': error, 'username': username, 'password': password}
        return render(request, 'user/login.html', context=context)

    username = request.COOKIES.get('username', '')
    context = {'title': '用户登录', 'error': error, 'username': username}
    return render(request, 'user/login.html', context=context)


def info(request):
    user = get_object_or_404(User, id=request.session.get('user_id'))
    context = {
        'title': '用户中心',
        'user_email': user.email,
        'user_name': request.session.get('user_name'),
    }
    return render(request, 'user/user_center_info.html', context=context)


def order(request):
    context = {
        'title': '用户订单',
    }
    return render(request, 'user/user_center_order.html', context=context)


def address(request):
    user = get_object_or_404(User, id=request.session.get('user_id'))
    contact = user.contact_set.order_by('id').all()
    if contact:
        contact = contact[0]
    else:
        contact = Contact(user=user, name='', address='', zip_code='', phone='')

    if request.method == 'POST':
        contact.name = request.POST.get('name')
        contact.address = request.POST.get('address')
        contact.zip_code = request.POST.get('zip_code')
        contact.phone = request.POST.get('phone')
        contact.save()
    context = {
        'title': '用户中心',
        'contact': contact,
    }
    return render(request, 'user/user_center_site.html', context=context)
