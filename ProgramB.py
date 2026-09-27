# @author Joao Felipe Ribeiro Neves - 61899
# @author Manuel Maria Ledo Fernandes Garrido de Figueiredo - 68264
#!/usr/bin/env python3
import sys
import requests
from urllib.parse import urljoin
import time

def fetch_manifest(server_url, movie_name):
    base = server_url.rstrip('/') + '/'
    url = urljoin(base, f"{movie_name}/manifest.txt")
    return requests.get(url).text

def parse_manifest(text):
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    num_tracks = int(lines[1])
    index = 2

    tracks = []
    for _ in range(num_tracks):
        file_name = lines[index]; index += 1
        index += 3                           
        nseg = int(lines[index]); index += 1

        segments = []
        for _ in range(nseg):
            off, size = lines[index].split()
            segments.append((int(off), int(size)))
            index += 1

        tracks.append((file_name, segments))

    return tracks

def download_track(server_url, movie_name, file_name, segments):
    base = server_url.rstrip('/') + '/'
    url = urljoin(base, f"{movie_name}/{file_name}")

    total_bytes = 0
    t0 = time.perf_counter()

    with open(file_name, "wb") as f:
        for offset, size in segments:
            r = requests.get(url, headers={"Range": f"bytes={offset}-{offset+size-1}"})
            f.write(r.content)
            total_bytes += len(r.content)

    elapsed = time.perf_counter() - t0
    rate = total_bytes / elapsed if elapsed > 0 else 0.0
    return elapsed, rate

def main():
    server_url, movie_name, out = sys.argv[1], sys.argv[2], sys.argv[3]

    text = fetch_manifest(server_url, movie_name)
    tracks = parse_manifest(text)

    with open(out, "w") as f:
        for file_name, segments in tracks:
            elapsed, rate = download_track(server_url, movie_name, file_name, segments)
            f.write(f"{elapsed}\n")
            f.write(f"{rate}\n")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 programB.py serverURL movieName resultsfile_name")
        sys.exit(1)
    main()
