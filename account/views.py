from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView,
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
)
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.core.signing import BadSignature, SignatureExpired, loads, dumps
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect, resolve_url
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import generic
from .forms import (
    LoginForm, UserCreateForm, UserUpdateForm, MyPasswordChangeForm,
    MyPasswordResetForm, MySetPasswordForm, EmailChangeForm
)

User = get_user_model()

class Login(LoginView):
    form_class = LoginForm
    template_name = 'login.html'

    def get(self, request, *args, **kwargs):
        # ログイン情報が入っていれば、リダイレクト
        if request.user.is_authenticated:
            return redirect('photo:home')
        else:
            params = {
                'form': self.form_class,
            }
            return render(request, self.template_name, context=params)

class Logout(LogoutView):
    template_name = 'logout.html'

class UserCreate(generic.CreateView):
    template_name = 'user_create.html'
    form_class = UserCreateForm

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        # アクティベーションURLの送付
        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': 'https' if self.request.is_secure() else 'http',
            'domain': domain,
            'token': dumps(user.pk),
            'user': user,
        }

        subject = render_to_string('mail_template/create/subject.txt', context)
        message = render_to_string('mail_template/create/message.txt', context)

        user.email_user(subject, message)
        return redirect('account:user_create_done')


class UserCreateDone(generic.TemplateView):
    template_name = 'user_create_done.html'


class UserCreateComplete(generic.TemplateView):
    template_name = 'user_create_complete.html'
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*60*24)

    def get(self, request, **kwargs):
        token = kwargs.get('token')
        try:
            user_pk = loads(token, max_age=self.timeout_seconds)

        # 期限切れ
        except SignatureExpired:
            return HttpResponseBadRequest()

        # tokenが間違っている
        except BadSignature:
            return HttpResponseBadRequest()

        # tokenは問題なし
        else:
            try:
                user = User.objects.get(pk=user_pk)
            except User.DoesNotExist:
                return HttpResponseBadRequest()
            else:
                if not user.is_active:
                    # まだ仮登録で、他に問題なければ本登録とする
                    user.is_active = True
                    user.save()
                    return super().get(request, **kwargs)

        return HttpResponseBadRequest()


class OnlyYouMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        user = self.request.user
        return user.pk == self.kwargs['pk'] or user.is_superuser

class PasswordChange(PasswordChangeView):
    form_class = MyPasswordChangeForm
    success_url = reverse_lazy('account:password_change_done')
    template_name = 'password_change.html'


class PasswordChangeDone(PasswordChangeDoneView):
    template_name = 'password_change_done.html'


class PasswordReset(PasswordResetView):
    subject_template_name = 'mail_template/password_reset/subject.txt'
    email_template_name = 'mail_template/password_reset/message.txt'
    template_name = 'password_reset_form.html'
    form_class = MyPasswordResetForm
    success_url = reverse_lazy('account:password_reset_done')


class PasswordResetDone(PasswordResetDoneView):
    template_name = 'password_reset_done.html'


class PasswordResetConfirm(PasswordResetConfirmView):
    form_class = MySetPasswordForm
    success_url = reverse_lazy('account:password_reset_complete')
    template_name = 'password_reset_confirm.html'


class PasswordResetComplete(PasswordResetCompleteView):
    template_name = 'password_reset_complete.html'


class EmailChange(LoginRequiredMixin, generic.FormView):
    template_name = 'email_change_form.html'
    form_class = EmailChangeForm

    def form_valid(self, form):
        user = self.request.user
        new_email = form.cleaned_data['email']

        # URLの送付
        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': 'https' if self.request.is_secure() else 'http',
            'domain': domain,
            'token': dumps(new_email),
            'user': user,
        }

        subject = render_to_string('mail_template/email_change/subject.txt', context)
        message = render_to_string('mail_template/email_change/message.txt', context)
        send_mail(subject, message, None, [new_email])

        return redirect('account:email_change_done')


class EmailChangeDone(LoginRequiredMixin, generic.TemplateView):
    template_name = 'email_change_done.html'


class EmailChangeComplete(LoginRequiredMixin, generic.TemplateView):
    template_name = 'email_change_complete.html'
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*60*24)  # デフォルトでは1日以内

    def get(self, request, **kwargs):
        token = kwargs.get('token')
        try:
            new_email = loads(token, max_age=self.timeout_seconds)

        # 期限切れ
        except SignatureExpired:
            return HttpResponseBadRequest()

        # tokenが間違っている
        except BadSignature:
            return HttpResponseBadRequest()

        # tokenは問題なし
        else:
            User.objects.filter(email=new_email, is_active=False).delete()
            request.user.email = new_email
            request.user.save()
            return super().get(request, **kwargs)