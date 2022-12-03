from django.shortcuts import render
from api.models import Task
from django.http import HttpResponseRedirect 
from .calendar_API import test_calendar

def todoappView(request):
    all_task_items = Task.objects.all()
    return render(request, 'index.html',
    {'all_items':all_task_items}) 

def addTodoView(request):
    x = request.POST['content']
    new_item = Task(title = x)
    new_item.save()
    return HttpResponseRedirect('/todoapp/')

def updateTodoView(request,i):
    x = request.POST['content']
    Task.objects.filter(id=i).update(title=x)
    return HttpResponseRedirect('/todoapp/')

def deleteTodoView(request, i):
    y = Task.objects.get(id= i)
    y.delete()
    return HttpResponseRedirect('/todoapp/') 


def demo(request):
    results = test_calendar()
    context = {"results": results}
    return render(request, 'demo.html', context)
