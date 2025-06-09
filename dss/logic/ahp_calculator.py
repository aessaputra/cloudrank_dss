import numpy as np

# Rasio Indeks Konsistensi Acak (Random Index) dari Saaty
# Kunci adalah jumlah kriteria (n), Nilai adalah RI
RANDOM_INDEX = {
    1: 0.00,
    2: 0.00,
    3: 0.58,
    4: 0.90,
    5: 1.12,
    6: 1.24,
    7: 1.32,
    8: 1.41,
    9: 1.45,
    10: 1.49,
    11: 1.51,
    12: 1.48,
    13: 1.56,
    14: 1.57,
    15: 1.59,
}

def calculate_ahp(comparison_matrix: list[list[float]]) -> dict:
    """
    Menghitung bobot kriteria dan rasio konsistensi menggunakan metode AHP.

    Args:
        comparison_matrix: Matriks perbandingan berpasangan (n x n) dalam format list of lists.

    Returns:
        Sebuah dictionary berisi:
        - 'weights': Bobot prioritas untuk setiap kriteria.
        - 'consistency_ratio': Rasio konsistensi (CR).
        - 'is_consistent': True jika CR <= 0.1, selain itu False.
    """
    matrix = np.array(comparison_matrix)
    n = matrix.shape[0]

    # 1. Normalisasi matriks dengan membagi setiap elemen dengan jumlah kolomnya
    col_sums = matrix.sum(axis=0)
    normalized_matrix = matrix / col_sums

    # 2. Hitung vektor prioritas (bobot) dengan merata-ratakan setiap baris
    weights = normalized_matrix.mean(axis=1)

    # 3. Hitung Rasio Konsistensi (CR)
    weighted_sum_vector = np.dot(matrix, weights)
    lambda_max = np.mean(weighted_sum_vector / weights)
    
    consistency_index = (lambda_max - n) / (n - 1) if n > 1 else 0.0

    # Ambil Random Index (RI) dari tabel
    random_index = RANDOM_INDEX.get(n, 1.59) # Default ke 1.59 jika n > 15
    
    if random_index == 0:
        consistency_ratio = 0.0 # Hindari pembagian dengan nol jika n=1 atau n=2
    else:
        consistency_ratio = consistency_index / random_index

    return {
        "weights": weights.tolist(),
        "consistency_ratio": consistency_ratio,
        "is_consistent": consistency_ratio <= 0.1,
    }