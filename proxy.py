# @author Joao Felipe Ribeiro Neves - 61899
# @author Manuel Maria Ledo Fernandes Garrido de Figueiredo - 68264
#!/usr/bin/env python3
import sys
import socket
import threading
import queue
import requests
from urllib.parse import urljoin

PLAYER_HOST = "localhost"
PLAYER_PORT = 8000

def fetch_manifest(server_url, movie_name):
    url = urljoin(server_url.rstrip("/") + "/", f"{movie_name}/manifest.txt")
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

def producer(q, server_url, movie_name, track_index):
    tracks = parse_manifest(fetch_manifest(server_url, movie_name))
    file_name, segments = tracks[track_index]

    base = server_url.rstrip("/") + "/"
    url = urljoin(base, f"{movie_name}/{file_name}")

    for offset, size in segments:
        r = requests.get(url, headers={"Range": f"bytes={offset}-{offset+size-1}"})
        q.put(r.content)

    q.put(None)

def consumer(q, sock):
    while True:
        data = q.get()
        if data is None:
            break
        sock.sendall(data)

def main():
    server_url = sys.argv[1]
    movie_name = sys.argv[2]
    track_index = int(sys.argv[3])

    q = queue.Queue(maxsize=10)

    sock = socket.socket()
    sock.connect((PLAYER_HOST, PLAYER_PORT))

    t_prod = threading.Thread(target=producer, args=(q, server_url, movie_name, track_index))
    t_cons = threading.Thread(target=consumer, args=(q, sock))

    t_prod.start()
    t_cons.start()
    t_prod.join()
    t_cons.join()

    try:
        sock.shutdown(socket.SHUT_WR)
    except:
        pass
    sock.close()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 proxy.py baseURL movieName track")
        sys.exit(1)
    main()
