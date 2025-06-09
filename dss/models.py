from django.db import models

# Model untuk menyimpan Kriteria
class Kriteria(models.Model):
    # Pilihan untuk atribut kriteria, 'benefit' atau 'cost'
    class Atribut(models.TextChoices):
        BENEFIT = 'benefit', 'Benefit'
        COST = 'cost', 'Cost'

    nama_kriteria = models.CharField(max_length=100, help_text="Nama kriteria (e.g., Biaya, Kinerja)")
    atribut = models.CharField(max_length=10, choices=Atribut.choices, help_text="Tipe kriteria: 'benefit' atau 'cost'")
    bobot = models.FloatField(default=0.0, help_text="Bobot kriteria hasil dari perhitungan AHP")

    def __str__(self):
        return self.nama_kriteria

    class Meta:
        verbose_name_plural = "Daftar Kriteria"


# Model untuk menyimpan Alternatif
class Alternatif(models.Model):
    nama_alternatif = models.CharField(max_length=100, help_text="Nama alternatif cloud (e.g., AWS, Azure, GCP)")

    def __str__(self):
        return self.nama_alternatif

    class Meta:
        verbose_name_plural = "Daftar Alternatif"