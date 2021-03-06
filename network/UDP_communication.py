import pickle
import socket
import struct
import threading
import zlib
import time

import numpy as np

FPS = 24
UDP_IP = '127.0.0.1'
UDP_PORT = 10000
MSG_CODE_SIZE = 4
MSG_SIZE_HEADER_SIZE = 8
MSG_CHUNK_SIZE = 1024
MAX_SIZE_UDP_MSG = 65507


# SERVER_IP = '127.0.0.1'
# SERVER_PORT = 11233


class UDPStream:

    def __init__(self, ip, frame_port, audio_port, FPS):
        self.udp_ip = ip
        self.udp_frame_port = frame_port
        self.udp_audio_port = audio_port
        self.participant_frame = None
        self.height = 480
        self.width = 640
        self.buf = 1024
        self.participant_track_chunks = [b'1'] * 500
        self.running = True
        self.received_frames = 0
        self.received_tracks = 0
        self.participant_track = None
        num_of_chunks = self.width * self.height * 3 / self.buf
        num_of_chunks = num_of_chunks * 0.15
        self.participant_frame_chunks = [b'\xc8\xcd\xdf\xc7\xcc\xde\xc6\xca\xde\xc6\xca\xde\xca\xca\xde\xca\xca\xde'
                                         b'\xca\xcc\xd7\xcb\xcd\xd8\xc8\xca\xde\xc5\xc8\xdc\xc8\xc7\xd7\xc8\xc7\xd7'
                                         b'\xc9\xca\xd9\xc9\xca\xd9\xc5\xc9\xd8\xc4\xc7\xd7\xc5\xc8\xdc\xc7\xc9\xdd'
                                         b'\xc5\xc8\xda\xc5\xc8\xda\xca\xc9\xd6\xc8\xc8\xd5\xcb\xc7\xd5\xcb\xc7\xd5'
                                         b'\xc7\xc6\xd6\xc7\xc6\xd6\xc8\xc6\xd1\xc7\xc4\xd0\xc8\xc5\xd5\xc8\xc5\xd5'
                                         b'\xc5\xc6\xd6\xc5\xc6\xd6\xc1\xc8\xd2\xc1\xc8\xd2\xc1\xc7\xd4\xc1\xc7\xd4'
                                         b'\xcb\xc7\xd1\xca\xc6\xcf\xc6\xc6\xd1\xc5\xc5\xd0\xc4\xc7\xcf\xc3\xc5\xce'
                                         b'\xc4\xc3\xcf\xc3\xc2\xce\xbd\xbf\xd4\xbe\xc1\xd5\xc0\xc3\xd1\xbe\xc2\xcf'
                                         b'\xc3\xc2\xcf\xc1\xc1\xce\xc1\xc1\xce\xbf\xbe\xcc\xb6\xba\xc9\xb5\xb8\xc8'
                                         b'\xb7\xb6\xc4\xb7\xb6\xc4\xb8\xba\xc6\xba\xbc\xc7\xbe\xbd\xcd\xc1\xc0\xd0'
                                         b'\xc4\xc2\xd2\xc4\xc2\xd2\xc4\xc0\xce\xc4\xc0\xce\xc3\xc1\xd3\xc5\xc3\xd5'
                                         b'\xc4\xc3\xd1\xc3\xc2\xcf\xbe\xc2\xd1\xbd\xc0\xd0\xc4\xc0\xd0\xc5\xc1\xd1'
                                         b'\xc1\xbf\xd4\xc1\xbf\xd4\xbc\xbf\xcf\xbd\xc0\xd0\xbf\xc0\xd0\xbf\xc0\xd0'
                                         b'\xb9\xc0\xd2\xb8\xbf\xd1\xc2\xbf\xcf\xc6\xc2\xd2\xc5\xc6\xd8\xc7\xc8\xda'
                                         b'\xc4\xc9\xd4\xc2\xc6\xd1\xc1\xc1\xd3\xbf\xc0\xd2\xbe\xbd\xcd\xb9\xb8\xc8'
                                         b'\xb9\xb6\xc2\xb7\xb4\xc0\xac\xb5\xc2\xaa\xb2\xbf\xac\xaf\xbf\xab\xae\xbd'
                                         b'\xb1\xae\xbc\xb1\xae\xbc\xac\xac\xb8\xac\xac\xb8\xa9\xab\xb6\xa8\xaa\xb5'
                                         b'\xa8\xaa\xb7\xa9\xab\xb8\xab\xaa\xba\xab\xaa\xba\xaf\xab\xb9\xaf\xab\xb9'
                                         b'\xac\xab\xbb\xab\xaa\xba\xac\xac\xb8\xac\xac\xb8\xaf\xac\xb8\xaf\xac\xb8'
                                         b'\xaa\xac\xb9\xaa\xac\xb9\xb0\xad\xbb\xb3\xb0\xbe\xae\xb0\xb9\xae\xb0\xb9'
                                         b'\xab\xae\xbd\xa9\xad\xbc\xb0\xb0\xb9\xb1\xb1\xba\xac\xb2\xc1\xac\xb2\xc1'
                                         b'\xb2\xb1\xbf\xb2\xb1\xbf\xb1\xb1\xbc\xb0\xb0\xbb\xb1\xb1\xba\xaf\xaf\xb8'
                                         b'\xb1\xb0\xbe\xb0\xaf\xbd\xae\xaf\xbf\xac\xac\xbc\xaa\xab\xbd\xad\xad\xbf'
                                         b'\xa8\xaf\xbc\xa7\xad\xbb\xb1\xae\xba\xb2\xaf\xbb\xb1\xad\xbd\xb2\xae\xbf'
                                         b'\xae\xaf\xbd\xad\xae\xbc\xa8\xaf\xba\xa7\xae\xb9\xac\xab\xbb\xae\xac\xbc'
                                         b'\xac\xab\xbd\xab\xa9\xbc\xb0\xaa\xba\xb1\xab\xbb\xaf\xac\xb8\xaf\xac\xb8'
                                         b'\xa8\xac\xb9\xa8\xac\xb9\xa6\xac\xbb\xa5\xab\xba\xab\xaa\xb8\xac\xac\xb9'
                                         b'\xa6\xa8\xbc\xa6\xa8\xbc\xac\xaa\xb5\xab\xa8\xb4\xab\xa8\xb6\xac\xa9\xb7'
                                         b'\xa6\xa7\xb7\xa7\xa8\xb8\xae\xaa\xb2\xae\xaa\xb2\xac\xa9\xb7\xab\xa8\xb6'
                                         b'\xa6\xa7\xb5\xa7\xa8\xb6\xab\xa8\xb4\xaa\xa7\xb3\xa2\xa6\xb5\xa2\xa6\xb5'
                                         b'\xa7\xa5\xb5\xa7\xa5\xb5\xa5\xa6\xb4\xa5\xa6\xb4\xa8\xa4\xb4\xa8\xa4\xb4'
                                         b'\xab\xa6\xb2\xaa\xa5\xb1\xa3\xa5\xb1\xa3\xa5\xb1\xa6\xa5\xb1\xa4\xa4\xaf'
                                         b'\xa6\xa5\xb2\xa6\xa5\xb2\xa1\xa2\xb2\xa1\xa2\xb2\xa4\xa3\xa8\xa6\xa5\xaa'
                                         b'\xa4\xa4\xaf\xa4\xa4\xaf\x9e\xa2\xad\x9f\xa3\xae\x9d\xa2\xb2\x9c\xa1\xb1'
                                         b'\xa1\xa1\xb4\xa0\xa0\xb2\xa5\x9f\xb1\xa5\x9f\xb1\x9f\xa0\xae\x9f\xa0\xae'
                                         b'\xa2\x9f\xab\xa2\x9f\xab\x9b\xa1\xae\x9b\xa1\xae\xa5\xa1\xaa\xa4\x9f\xa9'
                                         b'\xa1\xa1\xac\xa0\x9f\xab\xa1\x9e\xaa\xa1\x9e\xaa\x9f\x9d\xa7\xa1\x9f\xa8'
                                         b'\xa3\x9e\xaa\xa3\x9e\xaa\x9c\x9e\xab\x9a\x9c\xa9\x9a\x9b\xab\x9b\x9c\xac'
                                         b'\xa2\x9d\xa8\xa2\x9d\xa8\x9b\x9e\xa7\x9b\x9e\xa7\xa0\x9b\xa7\xa2\x9d\xa8'
                                         b'\x9c\x9e\xaa\x9b\x9d\xa8\x9a\x9f\xaa\x9a\x9f\xaa\x9d\x9e\xa5\x9b\x9c\xa3'
                                         b'\x9d\x9d\xaa\x9d\x9d\xaa\x9b\x9a\xa8\x9b\x9a\xa8\x9b\x9b\xa4\x9b\x9b\xa4'
                                         b'\x99\x9a\xaa\x99\x9a\xaa\x9d\x9a\xa6\x9c\x99\xa5\x98\x99\xa9\x99\x9a\xaa'
                                         b'\x9a\x99\xa7\x99\x98\xa6\x98\x9a\xa5\x98\x9a\xa5\x9a\x99\xa7\x9a\x99\xa7'
                                         b'\x98\x97\xa4\x98\x97\xa4\x97\x99\xa4\x95\x97\xa3\x9b\x98\xa4\x9a\x97\xa3'
                                         b'\x9a\x98\xa1\x98\x96\xa0\x94\x97\xa0\x94\x97\xa0\x96\x95\xa5\x96\x95\xa5'
                                         b'\x96\x95\xa5\x98\x96\xa6\x95\x97\xa3\x94\x96\xa1\x94\x96\xa1\x94\x96\xa1'
                                         b'\x99\x95\x9f\x9b\x96\xa0\x98\x96\xa0\x98\x96\xa0\x96\x97\xa0\x94\x94\x9d'
                                         b'\x93\x95\xa0\x94\x96\xa1\x93\x95\xa2\x94\x96\xa3\x92\x96\xa3\x92\x96\xa3'
                                         b'\x96\x97\x9e\x96\x97\x9e\x93\x96\x9f\x93\x96\x9f\x97\x96\x9b\x96\x95\x9a'
                                         b'\x94\x94\x9d\x94\x94\x9d\x95\x95\xa0\x95\x95\xa0\x95\x92\x9e\x94\x91\x9d'
                                         b'\x8d\x91\x9f\x90\x94\xa1\x90\x95\x9c\x8f\x94\x9a\x93\x91\xa2\x93\x91\xa2'
                                         b'\x94\x93\xa1\x93\x92\xa0\x96\x92\x99\x95\x91\x98\x94\x8f\x99\x96\x91\x9b'
                                         b'\x92\x91\x9d\x91\x90\x9c\x93\x90\x9c\x94\x91\x9d\x90\x92\x9d\x8e\x90\x9c'
                                         b'\x91\x90\x9c\x91\x90\x9c\x91\x91\x9a\x92\x92\x9b\x91\x91\x9a\x8f\x90\x99'
                                         b'\x95\x92\x93\x94\x91\x92\x94\x90\x97\x94\x90\x97\x96\x8f\x97\x96\x8f\x97'
                                         b'\x92\x8f\x99\x90\x8e\x98\x8f\x90\x99\x8f\x90\x99\x92\x90\x97\x92\x90\x97'
                                         b'\x8f\x8f\x9c\x8f\x8f\x9c\x94\x8f\x9a\x94\x8f\x9a\x8f\x90\x97\x91'] * int(
            num_of_chunks)
        self.user_frame = None
        self.lock = threading.Lock()
        self.FPS = FPS
        self.last = None
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_track(self, track, ip, port):
        buf = self.buf
        serialized = pickle.dumps(track)
        compressed = zlib.compress(serialized, 3)
        chunks = [compressed[i:i + buf] for i in range(0, len(compressed), buf)]

        addr = (ip, port)
        sock = self.sock

        last_index = len(chunks) - 1
        packed_last_index = struct.pack('!i', last_index)
        times_to_send = 1
        for j in range(times_to_send):
            for i in range(len(chunks)):
                packed_index = struct.pack('!i', i)
                sock.sendto(packed_index + packed_last_index + chunks[i], addr)

    def recv_track(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        addr = (self.udp_ip, self.udp_audio_port)
        sock.bind(addr)
        while self.running:
            packed_last_index = ""
            unpacked_last_index = 1
            unpacked_index = 0
            while unpacked_index < unpacked_last_index:
                chunk, _ = sock.recvfrom(self.buf + 8)
                packed_index = chunk[:4]
                unpacked_index = struct.unpack('!i', packed_index)[0]
                if packed_last_index != chunk[4:8]:
                    packed_last_index = chunk[4:8]
                    unpacked_new_last_index = struct.unpack('!i', packed_last_index)[0]
                    if unpacked_new_last_index > 0:
                        unpacked_last_index = unpacked_new_last_index
                # print(unpacked_index, packed_index, '/', unpacked_last_index, packed_last_index)
                chunk = chunk[8:]
                self.participant_track_chunks[unpacked_index] = chunk

            byte_track = b''.join(self.participant_track_chunks[:unpacked_last_index + 1])
            try:
                decompressed = zlib.decompress(byte_track)
                track = pickle.loads(decompressed)

                self.lock.acquire()
                self.participant_track = track
                self.received_tracks += 1
                self.lock.release()
            except zlib.error as e:
                print('Error: ', e)

    def send_frame(self, frame, ip, port):
        addr = (ip, port)
        buf = self.buf
        # code = 'start'
        # code = ('start' + (buf - len(code)) * 'a').encode('utf-8')
        sock = self.sock
        # sock.sendto(code, addr)
        d = frame.flatten()
        s = d.tostring()
        # print('\n\n\n\n frame => ', len(s))
        chunks = [s[i:i + buf] for i in range(0, len(s), buf)]
        # print(chunks[0])
        times_to_send = 2
        last_index = len(chunks) - 2
        packed_last_index = struct.pack('!i', last_index)
        # print('last index', last_index, packed_last_index)
        for j in range(times_to_send):
            for i in range(len(chunks)):
                if i > 0:
                    packed_index = struct.pack('!i', i - 1)
                    # print('index', i - 1, packed_index)
                    sock.sendto(packed_index + packed_last_index + chunks[i - 1], addr)
                    # sock.sendto(packed_index + packed_last_index + chunks[i - 1], addr)
            # if times_to_send > 1:
            #     time.sleep((1.0 / FPS) / (times_to_send - 1))


    def recv_frame(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        addr = (self.udp_ip, self.udp_frame_port)
        sock.bind(addr)
        num_of_chunks = self.width * self.height * 3 / self.buf
        # start_time = time.time()
        # x = 1  # displays the frame rate every 1 second
        # counter = 0
        while self.running:
            packed_last_index = ""
            unpacked_last_index = 1
            unpacked_index = 0
            # print('\n\nstart: ', unpacked_index, '/', unpacked_last_index, packed_last_index)
            chunks_received = 0
            while unpacked_index < unpacked_last_index:
                chunks_received += 1
                chunk, _ = sock.recvfrom(self.buf + 8)
                packed_index = chunk[:4]
                unpacked_index = struct.unpack('!i', packed_index)[0]
                if packed_last_index != chunk[4:8]:
                    packed_last_index = chunk[4:8]
                    unpacked_new_last_index = struct.unpack('!i', packed_last_index)[0]
                    if unpacked_new_last_index > 0:
                        unpacked_last_index = unpacked_new_last_index
                # print(unpacked_index, packed_index, '/', unpacked_last_index, packed_last_index)

                chunk = chunk[8:]
                if unpacked_index < len(self.participant_track_chunks):
                    self.participant_frame_chunks[unpacked_index] = chunk

            # print('end: ', unpacked_index, packed_index, '/', unpacked_last_index, packed_last_index)
            byte_frame = b''.join(self.participant_frame_chunks[:unpacked_last_index + 2])
            frame = byte_frame
            # frame = np.frombuffer(
            #     byte_frame, dtype=np.uint8).reshape(self.height, self.width, 3)
            self.lock.acquire()
            self.participant_frame = frame
            self.received_frames += 1
            self.lock.release()
            # counter += 1
            # if (time.time() - start_time) > x:
            #     print("FPS: ", counter / (time.time() - start_time))
            #     counter = 0
            #     start_time = time.time()

