from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse
from .models import Kriteria, Alternatif
from .logic.ahp_calculator import calculate_ahp
from .logic.topsis_calculator import calculate_topsis
from .models import Kriteria, Alternatif
from .forms import KriteriaForm, AlternatifForm
import numpy as np

def home_view(request):
    """
    Menampilkan halaman dashboard utama sebagai pusat navigasi.
    """
    kriteria_count = Kriteria.objects.count()
    alternatif_count = Alternatif.objects.count()
    context = {
        'kriteria_count': kriteria_count,
        'alternatif_count': alternatif_count,
    }
    return render(request, 'dss/home_dashboard.html', context)


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
    Menampilkan hasil akhir perankingan TOPSIS beserta grafiknya.
    """
    results_data = request.session.get('topsis_results', None)

    if not results_data:
        return redirect('home')

    scores = results_data['scores']
    alternatives = results_data['alternatives']
    
    # Gabungkan nama alternatif dengan skornya
    combined_results = zip(alternatives, scores)
    
    # Urutkan berdasarkan skor, dari tertinggi ke terendah
    # Kita perlu mengurutkan di sini SEBELUM memisahkannya untuk grafik
    final_results = sorted(combined_results, key=lambda x: x[1], reverse=True)

    # ✨ BAGIAN BARU: Siapkan data khusus untuk Chart.js ✨
    # Balikkan urutan agar di grafik bar horizontal, yang teratas adalah yang terbaik
    chart_labels = [result[0] for result in reversed(final_results)]
    chart_data = [result[1] for result in reversed(final_results)]

    context = {
        'final_results': final_results,
        'chart_labels': chart_labels, # Kirim daftar label ke template
        'chart_data': chart_data,   # Kirim daftar data skor ke template
    }
    
    # Hapus data dari session setelah digunakan
    if 'topsis_results' in request.session:
        del request.session['topsis_results']

    return render(request, 'dss/results.html', context)

def kriteria_list_view(request):
    """
    Menampilkan daftar semua kriteria yang ada di database.
    """
    semua_kriteria = Kriteria.objects.all().order_by('id')
    context = {
        'semua_kriteria': semua_kriteria,
    }
    return render(request, 'dss/kriteria_list.html', context)


def kriteria_create_view(request):
    """
    Menangani pembuatan kriteria baru.
    GET: Menampilkan form kosong.
    POST: Memproses data form dan menyimpan.
    """
    form = KriteriaForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('kriteria_list')

    context = {
        'form': form,
        'page_title': 'Tambah Kriteria Baru'
    }
    return render(request, 'dss/kriteria_form.html', context)


def kriteria_update_view(request, pk):
    """
    Menangani pembaruan kriteria yang sudah ada.
    """
    # Ambil objek kriteria berdasarkan pk, atau tampilkan 404 jika tidak ada
    kriteria_obj = get_object_or_404(Kriteria, pk=pk)

    # `instance=kriteria_obj` akan mengisi form dengan data yang ada
    form = KriteriaForm(request.POST or None, instance=kriteria_obj)
    
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('kriteria_list')

    context = {
        'form': form,
        'page_title': f'Edit Kriteria: {kriteria_obj.nama_kriteria}'
    }
    return render(request, 'dss/kriteria_form.html', context)

def kriteria_delete_view(request, pk):
    """
    Menangani penghapusan kriteria.
    GET: Menampilkan halaman konfirmasi.
    POST: Melakukan penghapusan dan redirect.
    """
    kriteria_obj = get_object_or_404(Kriteria, pk=pk)

    if request.method == 'POST':
        # Jika user mengkonfirmasi (mengirim form), hapus objek
        kriteria_obj.delete()
        # Arahkan kembali ke daftar kriteria
        return redirect('kriteria_list')

    context = {
        'kriteria': kriteria_obj
    }
    # Jika GET, tampilkan halaman konfirmasi
    return render(request, 'dss/kriteria_confirm_delete.html', context)

def alternatif_list_view(request):
    """
    Menampilkan daftar semua alternatif yang ada di database.
    """
    semua_alternatif = Alternatif.objects.all().order_by('id')
    context = {
        'semua_alternatif': semua_alternatif,
    }
    return render(request, 'dss/alternatif_list.html', context)

def alternatif_create_view(request):
    """
    Menangani pembuatan alternatif baru.
    """
    form = AlternatifForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('alternatif_list')

    context = {
        'form': form,
        'page_title': 'Tambah Alternatif Baru'
    }
    return render(request, 'dss/alternatif_form.html', context)

