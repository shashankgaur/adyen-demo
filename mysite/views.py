from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, JsonResponse
import Adyen
import requests, json
from ipware import get_client_ip
from random import randint
from .forms import PaymentForm, ColorfulPaymentForm
from django.core.files import File
from django.contrib import messages


merchant_account = "SupportRecruitementCOM"
apikey = "AQE1hmfxKo3NaxZDw0m/n3Q5qf3Ve55dHZxYTFdTxWq+l3JOk8J4BO7yyZBJ4o0JviXqoc8j9sYQwV1bDb7kfNy1WIxIIkxgBw==-q7XjkkN/Cud0WELZF+AzXpp/PuCB8+XmcdgqHYUWzTA=-Kk9N4dG837tIyjZF"
origin_key = "pub.v2.8115734003142692.aHR0cDovL2xvY2FsaG9zdDo4MDAw.1EveuPfJf3aj7AsulSgaDjkvHdHeF_fI1-W_EMtEACQ"



def _form_view(request, template_name='bootstrap4.html', form_class=PaymentForm):
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            pass
            #return render(request, template_name='checkout.html')
    else:
        form = form_class()
    return render(request, template_name, {'form': form})


def format_response(response):
    if "resultCode" in response:
        new_response = {"resultCode": response["resultCode"]}
        if "action" in response:
            new_response["action"] = response["action"]
        return json.dumps(new_response)
    else:
        raise PaymentError(response)

def handleShopperRedirect(request):
    values = request.json if request.is_json else request.values.to_dict()  # Get values from request object

    # Fetch paymentData from the frontend if we have not already
    if 'paymentData' in values:
        redirect_response = handle_shopper_redirect(values)
        if redirect_response["resultCode"] == 'Authorised':
            return render(request, 'success.html')
        elif redirect_response["resultCode"] == 'Received' or redirect_response["resultCode"] == 'Pending':
            return render(request, 'success.html')
        else:
            return render(request, 'failed.html')

def handle_shopper_redirect(values):
    url = "https://checkout-test.adyen.com/v52/payments/details"

    headers = {"X-Api-Key": apikey, "Content-type": "application/json"}

    print("/payments/details request:\n" + str(values))
    r = requests.post(url=url, headers=headers, json=values)
    print("/payments/details response:\n" + r.text)
    return loads(r.text)

def payments(frontend_request):
    url = "https://checkout-test.adyen.com/v52/payments"
    x_forwarded_for = frontend_request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = frontend_request.META.get('REMOTE_ADDR')
    
    headers = {"X-Api-Key": apikey, "Content-type": "application/json"}
    print(frontend_request)
    payment_methods_request = json.loads(frontend_request.body)

    payment_methods_request["amount"] = {"currency": "EUR",
                                         "value": "1000"}
    payment_methods_request["channel"] = "Web"
    payment_methods_request["shopperIP"] = str(ip)
    payment_methods_request["merchantAccount"] = "SupportRecruitementCOM"
    payment_methods_request["returnUrl"] = "http://localhost:8000/handleShopperRedirect"

    payment_methods_request["reference"] = 'Shashank Integration Test Reference' + str(randint(0, 10000))
    payment_methods_request["shopperReference"] = 'Python Checkout Shashank'
    payment_methods_request["additionalData"] = {"allow3DS2": "true", "executeThreeD": "true"}
    payment_methods_request["browserInfo"] = {"userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36",
                                            "acceptHeader": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                                            "language": "nl-NL",
                                            "colorDepth": 24,
                                            "screenHeight": 723,
                                            "screenWidth": 1536,
                                            "timeZoneOffset": 0,
                                            "javaEnabled": "true",
                                            }
    payment_methods_request["origin"] = "http://127.0.0.1:8000"
    payment_methods_request["countryCode"] = 'NL'
    payment_methods_request["shopperLocale"] = "en_US"


    print("/payments request:\n" + str(payment_methods_request))
    r = requests.post(url=url, headers=headers, json=payment_methods_request)
    text_response = r.text
    with open('data.txt', 'a') as outfile:
        json.dump(payment_methods_request, outfile)
        json.dump(r.json(), outfile)
    outfile.close()
    print("/payments response:\n" + text_response)

    return format_response(r.json())


# Custom payment error class
class PaymentError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

def payment_details(frontend_request):
    url = "https://checkout-test.adyen.com/v52/payments/details"

    headers = {"X-Api-Key": apikey, "Content-type": "application/json"}

    details = json.loads(frontend_request.body)

    print("/payments/details request:\n" + str(details))
    r = requests.post(url=url, headers=headers, json=details)
    response = r.text
    print("payments/details response:\n" + response)
    with open('data.txt', 'a') as outfile:
        json.dump(details, outfile)
        json.dump(r.json(), outfile)
    outfile.close()
    return response



def submitAdditionalDetails(request):
    details_response = payment_details(request)
    return HttpResponse(details_response, content_type='application/json')

def initiatePayment(request):
    print("initiating payment")
    payment_response = payments(request)
    return HttpResponse(payment_response, content_type='application/json')

def payment_methods():
    url = "https://checkout-test.adyen.com/v52/paymentMethods"
    headers = {"X-Api-Key": apikey, "Content-type": "application/json"}

    payment_methods_request = {}
    payment_methods_request["channel"] = "web"
    payment_methods_request["merchantAccount"] = "SupportRecruitementCOM"

    payment_methods_request["reference"] = 'Fusion paymentMethods call'

    print("/paymentMethods request:\n" + str(payment_methods_request))
    r = requests.post(url=url, headers=headers, json=payment_methods_request)
    response = r.text
    print("/paymentMethods response:\n" + response)
    with open('data.txt', 'a') as outfile:
        json.dump(payment_methods_request, outfile)
        json.dump(r.json(), outfile)
    outfile.close()
    return response

def checkout(request):
    payment_methods_response = payment_methods()
    context= {'payment_methods':payment_methods_response, 'origin_key':origin_key}
    return render(request, 'checkout.html', context)



def pending(request):
    return render(request, 'success.html')

def failed(request):
    return render(request, 'failed.html')


def error(request):
    return render(request, 'failed.html')

def success(request):
    return render(request, 'success.html')
def basic(request):
    return _form_view(request)

def manual(request):
    return render(request, template_name='success.html')

def manual(request):
    return _form_view(request, template_name='manual.html')


def field(request):
    return _form_view(request, template_name='field.html')


def attrs(request):
    return _form_view(request, form_class=ColorfulPaymentForm)


def tweaks(request):
    return _form_view(request, template_name='tweaks.html')


def bootstrap4(request):
    return _form_view(request, template_name='bootstrap4.html')

def user(request):
    return _form_view(request, template_name='user.html', form_class=UserCreationForm)
