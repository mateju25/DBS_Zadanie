from django.shortcuts import render


# vyrenderuje welcome stranku
def get_welcome_page(request):
    return render(request, 'welcome_page.html')
