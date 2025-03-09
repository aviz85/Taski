from django.shortcuts import render

# Create your views here.

def index(request):
    """
    הפונקציה שתציג את הדף הראשי של הממשק
    """
    return render(request, 'index.html')
