from django.shortcuts import render


def react_main(request):
    return render(request,'core/react-main.html')