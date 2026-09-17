# GPS SDR

A cold-start GPS L1 C/A signal detector (Gold-code correlation, Doppler/delay
search), from the FYS-3000 (Space Mission Design) course project.

## Layout

- [`goldcodes.py`](goldcodes.py) — GPS Gold-code generation
- [`gps_reception.py`](gps_reception.py) — GPS receiver signal processing (TLE-based satellite tracking, trilateration)
- [`test_deco.py`](test_deco.py) — cold-start detector: finds Doppler, PRN, and delay for all 32 constellation satellites

## Attribution

`goldcodes.py` and `gps_reception.py` are based on the
[`simple_gps_sdr`](https://github.com/jvierine) project by **Juha Vierinen**
(GitHub: jvierine), used here with permission. `test_deco.py` is an original
cold-start detector built on top of it.

## Data requirements

Raw GPS IQ sample captures (400+ MB) are **not included** — too large for a
git repo without LFS. Scripts expect a raw `complex64` IQ capture file
(10 MHz sample rate) in the working directory.

## Requirements

Scripts use `numpy`, `scipy`, `matplotlib`; `requests` and `sgp4`
(`gps_reception.py`'s TLE lookup).
