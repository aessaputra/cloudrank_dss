from django.contrib import admin
from .models import Kriteria, Alternatif

# Kustomisasi tampilan untuk model Kriteria di panel admin
class KriteriaAdmin(admin.ModelAdmin):
    list_display = ('nama_kriteria', 'atribut', 'bobot')
    list_filter = ('atribut',)
    search_fields = ('nama_kriteria',)

# Kustomisasi tampilan untuk model Alternatif
class AlternatifAdmin(admin.ModelAdmin):
    list_display = ('nama_alternatif',)
    search_fields = ('nama_alternatif',)

# Daftarkan model Anda di sini
admin.site.register(Kriteria, KriteriaAdmin)
admin.site.register(Alternatif, AlternatifAdmin)