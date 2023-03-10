from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import render, redirect

from contact.forms import ContactForm
from contact.models import Contact


def contact(request):
    if request.method == 'POST':

        form = ContactForm(request.POST)
        # secret_key = settings.RECAPTCHA_SECRET_KEY
        # data = request.POST
        # # captcha verification
        # data = {
        #     'response': data.get('g-recaptcha-response'),
        #     'secret': secret_key
        # }
        # resp = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        # result_json = resp.json()
        #
        # if not result_json.get('success'):
        #     messages.error(request, 'Duplicate mail or you are a robot')
        #     return redirect('blog:index')
        # end captcha verification

        # Validate the form: the captcha field will automatically
        # check the input
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            save_contact = Contact(name=name, subject=subject, email=email, message=message)

            save_contact.save()

            # Send mail
            send_mail(
                'Hej Knaldperle. Moses har spredt vandet igen med et Email mirakel fra WakeupDenmark',
                message,
                email,
                ['tbhedelund@gmail.com'],
                fail_silently=False
            )

            messages.success(request, 'Your message was sent.')
            return redirect('contact:contact')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})
