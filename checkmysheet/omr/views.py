from django.shortcuts import render

# Create your views here.
def index(request):
	return render(request,"<html><body><h1>hello</h1></body></html>",{})