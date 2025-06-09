# dss/views.py

from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from .models import Kriteria, Alternatif
from .logic.ahp_calculator import calculate_ahp
from .logic.topsis_calculator import calculate_topsis
import numpy as np

def home_view(request):
    """View sederhana untuk homepage."""
    # Di masa depan, ini bisa menjadi dashboard utama
    return redirect('ahp_matrix')


def ahp_view(request: HttpRequest) -> HttpResponse:
    kriteria_list = Kriteria.objects.all()
    n = kriteria_list.count()
    context = {'kriteria_list': kriteria_list}

    if n < 2:
        context['error_message'] = "Perlu minimal 2 kriteria untuk melakukan perbandingan AHP."
        return render(request, 'dss/ahp_matrix.html', context)

    if request.method == 'POST':
        matrix = np.ones((n, n))
        for i in range(n):
            for j in range(n):
                if i < j:
                    try:
                        val = float(request.POST.get(f'matrix_{i}_{j}', 1))
                        matrix[i, j] = val
                        matrix[j, i] = 1 / val
                    except (ValueError, TypeError):
                        context['error_message'] = "Pastikan semua input adalah angka yang valid."
                        return render(request, 'dss/ahp_matrix.html', context)
        
        ahp_result = calculate_ahp(matrix.tolist())
        
        if ahp_result['is_consistent']:
            for i, kriteria in enumerate(kriteria_list):
                kriteria.bobot = ahp_result['weights'][i]
                kriteria.save()
            
            # ✨ UBAH INI: Arahkan ke halaman input TOPSIS setelah AHP selesai
            return redirect('topsis_input') 
        else:
            cr_value = round(ahp_result['consistency_ratio'], 3)
            context['error_message'] = f"Matriks tidak konsisten! (CR = {cr_value}). Nilai CR harus <= 0.1."
            
    return render(request, 'dss/ahp_matrix.html', context)


def topsis_input_view(request: HttpRequest) -> HttpResponse:
    """
    Menampilkan form untuk input matriks keputusan TOPSIS dan memprosesnya.
    """
    alternatif_list = Alternatif.objects.all()
    kriteria_list = Kriteria.objects.all()
    context = {
        'alternatif_list': alternatif_list,
        'kriteria_list': kriteria_list,
    }

    if request.method == 'POST':
        # Bentuk matriks keputusan dari form
        decision_matrix = []
        for alt in alternatif_list:
            row = [float(request.POST.get(f'rating_{alt.id}_{kri.id}', 0)) for kri in kriteria_list]
            decision_matrix.append(row)
        
        # Ambil bobot dan atribut dari DB
        weights = [kri.bobot for kri in kriteria_list]
        attributes = [kri.atribut for kri in kriteria_list]

        # Panggil kalkulator TOPSIS
        topsis_result = calculate_topsis(decision_matrix, weights, attributes)

        # Simpan hasil ke session untuk ditampilkan di halaman hasil
        request.session['topsis_results'] = {
            'scores': topsis_result['performance_scores'],
            'alternatives': [alt.nama_alternatif for alt in alternatif_list]
        }
        
        return redirect('topsis_results')

    return render(request, 'dss/topsis_input.html', context)


def topsis_results_view(request: HttpRequest) -> HttpResponse:
    """
    Menampilkan hasil akhir perankingan TOPSIS.
    """
    results_data = request.session.get('topsis_results', None)

    if not results_data:
        # Jika tidak ada data di session, arahkan kembali ke awal
        return redirect('home')

    # Gabungkan nama alternatif dengan skornya dan urutkan
    scores = results_data['scores']
    alternatives = results_data['alternatives']
    
    final_results = sorted(zip(alternatives, scores), key=lambda x: x[1], reverse=True)

    context = {
        'final_results': final_results
    }
    
    # Hapus data dari session setelah ditampilkan
    del request.session['topsis_results']

    return render(request, 'dss/results.html', context)