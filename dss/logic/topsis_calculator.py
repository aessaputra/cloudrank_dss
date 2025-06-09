import numpy as np

def calculate_topsis(decision_matrix: list[list[float]], weights: list[float], attributes: list[str]) -> dict:
    """
    Menghitung peringkat alternatif menggunakan metode TOPSIS.

    Args:
        decision_matrix (list[list[float]]): Matriks keputusan (alternatif x kriteria).
        weights (list[float]): Bobot kriteria dari AHP.
        attributes (list[str]): Tipe atribut untuk setiap kriteria ('benefit' atau 'cost').

    Returns:
        dict: Berisi 'ranks' (indeks urutan) dan 'performance_scores' (nilai preferensi).
    """
    matrix = np.array(decision_matrix, dtype=float)
    w = np.array(weights, dtype=float)

    # 1. Normalisasi Matriks Keputusan
    norm_matrix = matrix / np.sqrt((matrix**2).sum(axis=0))

    # 2. Normalisasi Matriks Terbobot
    weighted_matrix = norm_matrix * w

    # 3. Tentukan Solusi Ideal Positif (A+) dan Solusi Ideal Negatif (A-)
    ideal_positive = np.zeros(matrix.shape[1])
    ideal_negative = np.zeros(matrix.shape[1])

    for j in range(matrix.shape[1]):
        if attributes[j].lower() == 'benefit':
            ideal_positive[j] = weighted_matrix[:, j].max()
            ideal_negative[j] = weighted_matrix[:, j].min()
        elif attributes[j].lower() == 'cost':
            ideal_positive[j] = weighted_matrix[:, j].min()
            ideal_negative[j] = weighted_matrix[:, j].max()

    # 4. Hitung Jarak ke Solusi Ideal Positif (D+) dan Negatif (D-)
    dist_positive = np.sqrt(((weighted_matrix - ideal_positive)**2).sum(axis=1))
    dist_negative = np.sqrt(((weighted_matrix - ideal_negative)**2).sum(axis=1))

    # 5. Hitung Nilai Preferensi (Skor Kinerja) untuk setiap Alternatif
    # Menambahkan epsilon kecil untuk menghindari pembagian dengan nol jika D+ + D- == 0
    epsilon = 1e-10 
    performance_scores = dist_negative / (dist_positive + dist_negative + epsilon)
    
    # 6. Rangking Alternatif (indeks dari skor tertinggi ke terendah)
    ranks = np.argsort(performance_scores)[::-1]

    return {
        "ranks": ranks.tolist(),
        "performance_scores": performance_scores.tolist(),
    }