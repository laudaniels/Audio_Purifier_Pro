import os
import time
import numpy as np
import scipy.signal as signal
import scipy.fft as fft
import soundfile as sf
import pyloudnorm as pyln

CACHE_DIR = '.cache'
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

class WAVPurifier:
    def __init__(self, ib, fn):
        self.input_bytes = bytearray(ib)
        self.filename = fn
        self.logs = []
        self.chunks = []
        self.metadata_details = {"deleted": {}, "kept": {}}
        self.ai_phase = False
        self.orig_data = None
        self.sr = None
        self.data = None

    def log(self, m): 
        self.logs.append(f'[{time.strftime("%H:%M:%S")}] {m}')

    def scan(self):
        # Reset metadata details
        self.metadata_details = {"deleted": {}, "kept": {}}
        self.chunks = []

        # 1. Scan standaard RIFF/WAV chunks
        riff_targets = {
            b'LIST': 'LIST (RIFF Informatie Container)',
            b'INFO': 'INFO (Algemene info)',
            b'IART': 'IART (Artist info)',
            b'ICMT': 'ICMT (Comment info)',
            b'c2pa': 'c2pa (Cryptografische AI-Tracking)',
            b'TC260': 'TC260 (AI Layout Manifest)',
            b'acid': 'acid (DAW Beatgrid & Loop-parameters)'
        }

        for chunk_bytes, chunk_label in riff_targets.items():
            idx = self.input_bytes.find(chunk_bytes)
            if idx != -1:
                self.chunks.append(chunk_bytes.decode(errors='ignore').strip())
                try:
                    chunk_len = int.from_bytes(self.input_bytes[idx+4:idx+8], byteorder='little')
                    if 4 < chunk_len < 2048:
                        raw_payload = self.input_bytes[idx+8:idx+8+chunk_len]
                        clean_text = "".join([chr(b) for b in raw_payload if 32 <= b <= 126]).strip()
                        
                        if chunk_bytes == b'acid':
                            self.metadata_details["kept"][chunk_label] = "Actief (DAW Beatgrid intact)"
                        else:
                            val = clean_text if clean_text else "Aanwezig (Binaire data)"
                            self.metadata_details["deleted"][chunk_label] = val
                except:
                    if chunk_bytes == b'acid':
                        self.metadata_details["kept"][chunk_label] = "Actief"

        # 2. Diepe scan binnen de 'id3 ' container voor sub-tags
        id3_idx = self.input_bytes.find(b'id3 ')
        if id3_idx != -1:
            self.chunks.append('id3')
            id3_payload = self.input_bytes[id3_idx+8:id3_idx+4096]
            
            sub_tags = {
                'TIT2': ('TIT2 (Title)', 'deleted'),
                'TPE1': ('TPE1 (Artist)', 'deleted'),
                'COMM': ('COMM (Comment)', 'deleted'),
                'TBPM': ('TBPM (BPM)', 'kept'),
                'TKEY': ('TKEY (Key)', 'kept')
            }
            
            for sub_bytes, (sub_label, action) in sub_tags.items():
                sub_idx = id3_payload.find(sub_bytes.encode())
                if sub_idx != -1:
                    try:
                        raw_txt = id3_payload[sub_idx+10:sub_idx+70]
                        clean_txt = "".join([chr(b) for b in raw_txt if 32 <= b <= 126]).strip()
                        clean_txt = "".join(c for c in clean_txt if c.isalnum() or c in '() -_.:/+=&')
                        for k in sub_tags.keys():
                            clean_txt = clean_txt.replace(k, "")
                        
                        val = clean_txt.strip() if clean_txt.strip() else "Gedetecteerd"
                        self.metadata_details[action][sub_label] = val
                    except:
                        self.metadata_details[action][sub_label] = "Gedetecteerd"

        tn = os.path.join(CACHE_DIR, f'temp_scan_{self.filename}')
        with open(tn, 'wb') as f: 
            f.write(self.input_bytes)
        try:
            d, sr = sf.read(tn, dtype='float32')
            self.sr = sr
            if len(d.shape) == 1:
                d = np.vstack((d, d)).T
            self.orig_data = d.copy()
            if len(d.shape) == 2:
                if np.corrcoef(d[:, 0], d[:, 1]) > 0.98: 
                    self.ai_phase = True
        except: 
            pass
        finally:
            if os.path.exists(tn): 
                os.remove(tn)
        return self.chunks, self.ai_phase, self.metadata_details

    def strip(self):
        for t in [b'LIST', b'INFO', b'IART', b'ICMT', b'c2pa', b'TC260']:
            idx = 0
            while True:
                idx = self.input_bytes.find(t, idx)
                if idx == -1: break
                self.log(f'Neutralizing RIFF chunk: {t.decode(errors="ignore")} -> JUNK')
                self.input_bytes[idx:idx+4] = b'JUNK'
                idx += 4

        id3_idx = self.input_bytes.find(b'id3 ')
        if id3_idx != -1:
            for sub_tag in [b'TIT2', b'TPE1', b'COMM']:
                idx = id3_idx
                while True:
                    idx = self.input_bytes.find(sub_tag, idx, id3_idx + 4096)
                    if idx == -1: break
                    self.log(f'Neutralizing ID3 Sub-tag: {sub_tag.decode()} -> JUNK')
                    self.input_bytes[idx:idx+4] = b'JUNK'
                    idx += 4
# =====================================================================
    def purify_with_gate(self, db_threshold, s, w, l, shimmer_amount, status_callback=None):
        try:
            saved_chunks = []
            for target in [b'id3 ', b'acid']:
                idx = self.input_bytes.find(target)
                if idx != -1:
                    try:
                        c_len = int.from_bytes(self.input_bytes[idx+4:idx+8], byteorder='little')
                        if target == b'id3 ': c_len = 4096 
                        chunk_data = self.input_bytes[idx:idx+8+c_len]
                        saved_chunks.append(chunk_data)
                    except:
                        pass

            tn = os.path.join(CACHE_DIR, f'temp_in_{self.filename}')
            with open(tn, 'wb') as f: 
                f.write(self.input_bytes)
            d, sr = sf.read(tn, dtype='float32')
            if os.path.exists(tn): 
                os.remove(tn)
            if len(d.shape) == 1: 
                d = np.vstack((d, d)).T
                
            self.log(f'Initializing 2D Gevectoriseerde STFT Matrix Engine...')
            if status_callback: status_callback("⏳ Generating STFT Spectral Matrix...", "running")
                
            linear_threshold = 10 ** (db_threshold / 20.0)
            nfft, hop, window = 2048, 512, 'hann'
            
            freqs = fft.fftfreq(nfft, 1/sr)[:nfft//2 + 1]
            freqs = np.abs(freqs)
            ai_target_frequencies = np.concatenate((np.linspace(18000, 22000, 41), np.linspace(20, 150, 14)))
            
            is_target = np.zeros_like(freqs, dtype=bool)
            for target in ai_target_frequencies:
                is_target |= (np.abs(freqs - target) < 150)
                
            f_axis, t_axis, Zxx = signal.stft(d.T, fs=sr, window=window, nperseg=nfft, noverlap=nfft-hop, boundary='zeros', padded=True)
            mag = np.abs(Zxx) / (nfft / 2)
            gate_mask = is_target[:, np.newaxis] & (mag < linear_threshold)
            Zxx[gate_mask] *= 0.05
            
            _, pd_transposed = signal.istft(Zxx, fs=sr, window=window, nperseg=nfft, noverlap=nfft-hop, boundary='zeros')
            self.data = pd_transposed.T[:d.shape[0], :]
            self.sr = sr

            if shimmer_amount > 0:
                for ch in range(self.data.shape[1]):
                    cutoff = 16000 - (shimmer_amount * 4000)
                    b, a = signal.butter(4, cutoff / (self.sr / 2), btype='low')
                    self.data[:, ch] = signal.filtfilt(b, a, self.data[:, ch])

            if s > 0: self.data = np.tanh(self.data * (1.0 + s * 0.5))
            if self.data.shape[1] == 2:
                mid = 0.5 * (self.data[:, 0] + self.data[:, 1])
                side = 0.5 * (self.data[:, 0] - self.data[:, 1]) * w
                self.data[:, 0] = mid + side
                self.data[:, 1] = mid - side
                
            try:
                m = pyln.Meter(sr)
                ld = m.integrated_loudness(self.data)
                normalized_data = pyln.normalize.loudness(self.data, ld, l)
                max_peak = np.max(np.abs(normalized_data))
                self.data = (normalized_data / max_peak) * 0.841 if max_peak > 0.841 else normalized_data
            except:
                mv = np.max(np.abs(self.data))
                if mv > 0: self.data = (self.data / mv) * 0.841
                    
            self.data = np.clip(self.data, -0.99, 0.99)
            
            raw_name, _ = os.path.splitext(self.filename)
            to = os.path.join(CACHE_DIR, f'purified_{raw_name}.wav')
            sf.write(to, self.data, sr, subtype='PCM_16')
            
            with open(to, 'rb') as f: 
                clean_wav_bytes = bytearray(f.read())
            if os.path.exists(to): 
                os.remove(to)
                
            if saved_chunks:
                self.log(f'Re-injecting kept metadata chunks ({len(saved_chunks)})...')
                for chunk in saved_chunks:
                    clean_wav_bytes.extend(chunk)
                
                new_size = len(clean_wav_bytes) - 8
                clean_wav_bytes[4:8] = new_size.to_bytes(4, byteorder='little')

            self.log('🚀 Optimization & custom metadata injection completed.')
            return bytes(clean_wav_bytes), self.logs, self.data

        except Exception as global_err:
            empty_audio = np.zeros((44100, 2), dtype=np.float32)
            return b'', [f'Error: {global_err}'], empty_audio
