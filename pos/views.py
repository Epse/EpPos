from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return HttpResponse("Hello World. This is the pos starting page")

def order(request):
    return HttpResponse("Hello. Here you would be able to take an order")

def addition(request):
    return HttpResponse("Hello. Here you will be able to see the order, as well as the due amount")
