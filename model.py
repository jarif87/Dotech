# signature_verifier/models.py
from django.db import models
import cv2
import numpy as np
from PIL import Image
import io
from django.core.files.base import ContentFile

class Signature(models.Model):
    name = models.CharField(max_length=100)
    original_signature = models.ImageField(upload_to='original_signatures/')
    verification_signature = models.ImageField(upload_to='verification_signatures/', null=True, blank=True)
    match_percentage = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def preprocess_image(self, image_field):
        # Read image and convert to grayscale
        image = Image.open(image_field)
        image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
        
        # Apply threshold to get binary image
        _, binary = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
        
        # Remove noise
        kernel = np.ones((5,5), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        return binary

    def compare_signatures(self):
        if not self.verification_signature:
            return None

        # Preprocess both signatures
        original = self.preprocess_image(self.original_signature)
        verification = self.preprocess_image(self.verification_signature)

        # Resize images to same size
        verification = cv2.resize(verification, (original.shape[1], original.shape[0]))

        # Calculate similarity using various methods
        try:
            # Structural Similarity Index
            score = cv2.matchTemplate(original, verification, cv2.TM_CCOEFF_NORMED)
            match_percentage = float(score.max()) * 100
            
            # Update match percentage
            self.match_percentage = match_percentage
            self.save()
            
            return match_percentage
        except Exception as e:
            print(f"Error comparing signatures: {e}")
            return None

# signature_verifier/views.py
from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, DetailView
from .models import Signature
from .forms import SignatureForm
from django.urls import reverse_lazy

class SignatureListView(ListView):
    model = Signature
    template_name = 'signature_verifier/signature_list.html'
    context_object_name = 'signatures'

class SignatureCreateView(CreateView):
    model = Signature
    form_class = SignatureForm
    template_name = 'signature_verifier/signature_form.html'
    success_url = reverse_lazy('signature-list')

class SignatureDetailView(DetailView):
    model = Signature
    template_name = 'signature_verifier/signature_detail.html'

def verify_signature(request, pk):
    signature = Signature.objects.get(pk=pk)
    if request.method == 'POST' and request.FILES.get('verification_signature'):
        signature.verification_signature = request.FILES['verification_signature']
        signature.save()
        match_percentage = signature.compare_signatures()
        return redirect('signature-detail', pk=pk)
    return redirect('signature-detail', pk=pk)

# signature_verifier/forms.py
from django import forms
from .models import Signature

class SignatureForm(forms.ModelForm):
    class Meta:
        model = Signature
        fields = ['name', 'original_signature']

# signature_verifier/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.SignatureListView.as_view(), name='signature-list'),
    path('create/', views.SignatureCreateView.as_view(), name='signature-create'),
    path('signature/<int:pk>/', views.SignatureDetailView.as_view(), name='signature-detail'),
    path('signature/<int:pk>/verify/', views.verify_signature, name='signature-verify'),
]