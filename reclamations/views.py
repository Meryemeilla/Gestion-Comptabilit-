from django.shortcuts import render, redirect
from .forms import ReclamationForm

def create(request):
    if request.method == 'POST':
        form = ReclamationForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('cabinet:reclamation_list')
    else:
        form = ReclamationForm(user=request.user)
    return render(request, 'reclamations/form.html', {'form': form})
