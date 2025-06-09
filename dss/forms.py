from django import forms
from .models import Kriteria

class KriteriaForm(forms.ModelForm):
    class Meta:
        model = Kriteria
        # Kita hanya butuh input untuk nama dan atribut.
        # Bobot akan dihitung oleh AHP, jadi tidak dimasukkan ke form.
        fields = ['nama_kriteria', 'atribut']
        widgets = {
            'nama_kriteria': forms.TextInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Contoh: Biaya, Kinerja, Keamanan'
            }),
            'atribut': forms.Select(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500'
            }),
        }
        labels = {
            'nama_kriteria': 'Nama Kriteria',
            'atribut': 'Tipe Atribut',
        }