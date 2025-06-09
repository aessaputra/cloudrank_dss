from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from .models import Kriteria
from .logic.ahp_calculator import calculate_ahp
import numpy as np

def ahp_view(request: HttpRequest) -> HttpResponse:
    """
    Menampilkan dan memproses matriks perbandingan berpasangan AHP.
    """
    kriteria_list = Kriteria.objects.all()
    n = kriteria_list.count()
    context = {
        'kriteria_list': kriteria_list,
    }

    if n < 2:
        context['error_message'] = "Perlu minimal 2 kriteria untuk melakukan perbandingan AHP."
        return render(request, 'dss/ahp_matrix.html', context)

    if request.method == 'POST':
        # Bentuk kembali matriks dari data form
        matrix = np.ones((n, n))
        for i in range(n):
            for j in range(n):
                if i < j:
                    try:
                        val = float(request.POST.get(f'matrix_{i}_{j}', 1))
                        matrix[i, j] = val
                        matrix[j, i] = 1 / val
                    except (ValueError, TypeError):
                        # Jika ada input yang tidak valid, kembali dengan error
                        context['error_message'] = "Pastikan semua input adalah angka yang valid."
                        return render(request, 'dss/ahp_matrix.html', context)
        
        # Hitung AHP menggunakan logika yang sudah dibuat
        ahp_result = calculate_ahp(matrix.tolist())
        
        if ahp_result['is_consistent']:
            # Jika konsisten, simpan bobot ke database
            for i, kriteria in enumerate(kriteria_list):
                kriteria.bobot = ahp_result['weights'][i]
                kriteria.save()
            
            # Arahkan ke langkah selanjutnya (TOPSIS)
            return redirect('home')
        else:
            # Jika tidak konsisten, tampilkan pesan error
            cr_value = round(ahp_result['consistency_ratio'], 3)
            context['error_message'] = f"Matriks tidak konsisten! (CR = {cr_value}). Nilai CR harus <= 0.1. Mohon perbaiki nilai perbandingan Anda."
            
    return render(request, 'dss/ahp_matrix.html', context)

def home_view(request):
    """View sederhana untuk homepage."""
    return render(request, 'dss/home.html')