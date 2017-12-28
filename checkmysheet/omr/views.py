from django.shortcuts import render
from django.http import HttpResponse
from .forms import PostForm

# Create your views here.
def index(request):
	form = PostForm(request.POST or None,request.FILES or None)
	context = {'status':'not working'}
	if form.is_valid():
		context['status'] = 'working'
	return render(request,"index.html",context)