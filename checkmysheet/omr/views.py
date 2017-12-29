from django.shortcuts import render
from django.http import HttpResponse
from .forms import PostForm

# Create your views here.
# def index(request):
# 	form = PostForm(request.POST or None,request.FILES or None)
# 	context = {'status':'not working'}
# 	if form.is_valid():
# 		context['status'] = 'working'
# 	return render(request,"index.html",context)

def create(request):
	form = PostForm(request.POST or None,request.FILES or None)
	context = {'form':form,'status':'not working'}
	if form.is_valid():
		instance = form.save(commit=False)
		instance.save()
		context['status'] = 'working'
		
	return render(request,"create.html",context)