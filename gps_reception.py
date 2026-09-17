import requests
import numpy as np
import matplotlib.pyplot as plt
import goldcodes as gc
import scipy.signal.windows as sw
import scipy as s
from sgp4.api import Satrec, SatrecArray
from datetime import datetime

# Constants
sr = 10e6  # Sample rate
dec = 10  # Decimation for delays
n_samples = 20 * 10000  # Number of samples to process
code_length = 10e6 * 1023 / 1.023e6  # GPS code length
code_lengthi = int(np.ceil(10e6 * 1023 / 1.023e6))  # Integer code length

# Download TLE data from Celestrak GPS-OPS group
tle_url = "https://celestrak.org/NORAD/elements/gp.php?GROUP=GPS-OPS&FORMAT=TLE"
response = requests.get(tle_url)
tle_data = response.text.splitlines()

# Parse TLE data into Satrec objects
satellites = []
for i in range(0, len(tle_data), 3):
    sat_name = tle_data[i]
    tle_line1 = tle_data[i + 1]
    tle_line2 = tle_data[i + 2]
    satellite = Satrec.twoline2rv(tle_line1, tle_line2)
    satellites.append(satellite)


# GPS signal processing parameters
def lpf(fc=0.8e6, sr=10e6, N=500):
    om0 = 2 * np.pi * fc / sr
    m = np.arange(-N, N) + 1e-6
    return np.array(sw.hann(len(m)) * np.sin(m * om0) / (np.pi * m), dtype=np.float32)


# Read data from GPS receiver (binary data, assumed to be in complex format)
f = open("gps_data.dat", "rb")
z = np.fromfile(f, count=n_samples, dtype=np.complex64)
print(len(z))

# Filter for signal processing
w = lpf()
W = s.fft.fft(w, n_samples)

# Perform the usual signal processing steps
MFI = np.zeros([len(satellites), n_samples, code_lengthi], dtype=np.float32)
for di in range(n_samples):
    zdc = z * np.exp(1j * 2 * np.pi * di * np.arange(n_samples) / sr)
    ZDC = s.fft.fft(zdc)

    # Process the GPS signal with Gold codes (GCM)
    GCM = gc.get_gps_codes(n_samples, n_coh=4)
    CC = s.fft.ifft(ZDC[None, :] * GCM, axis=1)
    PWR = np.real(CC * np.conj(CC))

    for ri in range(n_reps):
        MFI[:, di, :] += PWR[:, clidx + int(ri * code_length)]

# Now, for each satellite, compute the Doppler shift and delay
sat_positions = []
for satellite in satellites:
    # TLE data gives satellite's orbital parameters
    # We need to calculate the position and velocity at the time of the measurement
    ts = datetime.utcnow()
    jd = ts.toordinal() + 1721424.5 + ts.hour / 24 + ts.minute / 1440 + ts.second / 86400
    satellite_epoch = satellite.sgp4(jd)
    sat_pos, sat_vel = satellite_epoch[0], satellite_epoch[1]

    # Convert position to ECEF coordinates (in meters)
    sat_positions.append(sat_pos)


# Estimate the receiver's position using trilateration with at least 4 satellites
def trilateration(sat_positions, delays):
    # We need at least 4 satellites for trilateration
    if len(sat_positions) < 4:
        raise ValueError("At least 4 satellites are needed for trilateration.")

    # Use the positions and delays to estimate the receiver's position
    # This is a simplified example using least-squares, assuming spherical geometry
    A = np.array([[sat[0] - sat_positions[0][0], sat[1] - sat_positions[0][1], sat[2] - sat_positions[0][2]] for sat in
                  sat_positions])
    b = np.array([delays[i] for i in range(len(delays))])

    # Solve the system A * x = b using least squares
    receiver_position = np.linalg.lstsq(A, b, rcond=None)[0]
    return receiver_position


# Example satellite delays in seconds (you would get these from signal processing)
delays = [0.1, 0.15, 0.2, 0.25]  # Example delays from 4 satellites

# Estimate the receiver's location
receiver_position = trilateration(sat_positions, delays)
print("Estimated Receiver Position: ", receiver_position)

f.close()
