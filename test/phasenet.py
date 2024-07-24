import numpy as np
import obspy
from seisbench.models import PhaseNet

print("Contoh penggunaan PhaseNet:")
# Langkah 1: Muat Model
model = PhaseNet.from_pretrained("instance")

print("Model berhasil dimuat.")
# Langkah 2: Persiapkan Data
data = np.random.randn(3 * 1000 * 3)  # Contoh data seismogram

# convert to ObsPy Stream
data = obspy.Stream([obspy.Trace(data)])

print("Data seismogram berhasil disiapkan.")
# Langkah 3: Prediksi Menggunakan PhaseNet
predictions = model.classify(data)

print(predictions)