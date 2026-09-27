# @author Joao Felipe Ribeiro Neves - 61899
# @author Manuel Maria Ledo Fernandes Garrido de Figueiredo - 68264
#!/usr/bin/env python3
import sys
import requests
from urllib.parse import urljoin

def fetch_manifest(server_url, movie_name):
    url = urljoin(server_url.rstrip('/') + '/', f"{movie_name}/manifest.txt")
    return requests.get(url).text

def parse_manifest(text):
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

    movie_name = lines[0]
    num_tracks = int(lines[1])

    index = 2
    track_totals = []
    num_segments = None

    for _ in range(num_tracks):
        index += 4

        seg_count = int(lines[index])
        index += 1

        if num_segments is None:
            num_segments = seg_count

        total = 0
        for _ in range(seg_count):
            _, size = lines[index].split()
            total += int(size)
            index += 1

        track_totals.append(total)

    return num_tracks, num_segments, track_totals

def write_results(path, num_tracks, num_segments, totals):
    with open(path, "w") as f:
        f.write(str(num_tracks) + "\n")
        f.write(str(num_segments) + "\n")
        for track in totals:
            f.write(str(track) + "\n")

def main():
    server_url, movie_name, out = sys.argv[1], sys.argv[2], sys.argv[3]
    text = fetch_manifest(server_url, movie_name)
    num_tracks, num_segments, totals = parse_manifest(text)
    write_results(out, num_tracks, num_segments, totals)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 programA.py serverURL movieName resultsFileName")
        sys.exit(1)
    main()
