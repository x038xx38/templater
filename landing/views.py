from django.shortcuts import render

def index(request):
    template = 'landing.html'
    context = {}
    return render(request, template, context)
