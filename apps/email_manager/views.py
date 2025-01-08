from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.core.mail import send_mail, BadHeaderError
from .models import SMTPSettings
from .forms import SMTPConfigurationForm

@login_required
def smtp_config(request):
    try:
        config = SMTPSettings.objects.get(user=request.user)
    except SMTPSettings.DoesNotExist:
        config = None

    if request.method == 'POST':
        form = SMTPConfigurationForm(request.POST, instance=config)
        if form.is_valid():
            config = form.save(commit=False)
            config.user = request.user
            config.save()
            return redirect('smtp_config')
    else:
        form = SMTPConfigurationForm(instance=config)

    return render(request, 'email_manager/smtp_config.html', {'form': form})

@login_required
@require_POST
def test_smtp_config(request):
    try:
        config = SMTPSettings.objects.get(user=request.user)
    except SMTPSettings.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'SMTP configuration not found'})

    try:
        send_mail(
            subject='Test Email',
            message='This is a test email from your MailConnect application.',
            from_email=config.username,
            recipient_list=[request.user.email],
            fail_silently=False,
        )
        return JsonResponse({'success': True, 'message': 'Test email sent successfully'})
    except BadHeaderError:
        return JsonResponse({'success': False, 'message': 'Invalid header found in email'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})