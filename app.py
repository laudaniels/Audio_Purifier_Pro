import os
import glob
import time
import numpy as np
import streamlit as st

from styles import CUSTOM_CSS, PRESETS
from core import WAVPurifier, CACHE_DIR

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.title('🎛️ Audio Purifier Pro')
st.subheader('Dynamic Spectral Gating & Waveform Analysis')

uf = st.file_uploader('Upload a WAV...', type=['wav'])

if uf is not None:
    if 'purifier' not in st.session_state or st.session_state.current_file != uf.name:
        st.session_state.purifier = WAVPurifier(uf.read(), uf.name)
        st.session_state.current_file = uf.name
        st.session_state.chunks, st.session_state.ai_phase, st.session_state.meta_details = st.session_state.purifier.scan()
        if 'clean_bytes' in st.session_state:
            del st.session_state.clean_bytes
        
    st.markdown('### 📊 Scan Summary & Metadata Breakdown')
    p_text = 'High probability of rigid AI layout detected.' if st.session_state.ai_phase else 'Phase correlation looks organic.'
    
    # HTML Layout voor overzichtelijke splitsing van tags en hun inhoud
    summary_html = f'<div class="summary-box"><b>Bestand:</b> {uf.name}<br>'
    summary_html += f'<b>Phase Grid Analysis:</b> {p_text}<br><br>'
    
    # 1. Toon te verwijderen items
    summary_html += '<b style="color: #f87171;">🔴 Verwijderde Metadata & Containers (Wordt Gestript):</b><br>'
    if st.session_state.meta_details.get("deleted"):
        for tag, value in st.session_state.meta_details["deleted"].items():
            summary_html += f'• <u>{tag}</u> ➜ <span class="meta-content" style="color:#fca5a5;"> {value}</span><br>'
    else:
        summary_html += '• <i>Geen destructieve tags gevonden.</i><br>'
        
    # 2. Toon permanent te behouden items
    summary_html += '<br><b style="color: #4ade80;">🟢 Behouden Metadata & Containers (Volledig Intact):</b><br>'
    if st.session_state.meta_details.get("kept"):
        for tag, value in st.session_state.meta_details["kept"].items():
            summary_html += f'• <u>{tag}</u> ➜ <span class="meta-content" style="color:#86efac; font-weight:bold;"> {value}</span><br>'
    else:
        summary_html += '• <i>Geen muzikale herkenningstags (BPM/Key/Grid) aanwezig.</i><br>'
        
    summary_html += '</div>'
    st.markdown(summary_html, unsafe_allow_html=True)
    
    st.markdown('### ⚙️ Adjust & Real-Time Preview')
    sp = st.selectbox('Choose Stem Preset:', options=list(PRESETS.keys()), index=0)
    pv = PRESETS[sp]
    
    cl1, cl2 = st.columns(2)
    with cl1:
        threshold = st.slider('Spectral Gate Threshold (dB)', -80.0, -20.0, value=float(pv['threshold']), step=1.0)
        target_lufs = st.slider('Target Loudness (LUFS)', -20.0, -10.0, value=float(pv['lufs']), step=1.0)
    with cl2:
        saturation = st.slider('Analog Tape Warmth', 0.0, 1.0, value=float(pv['saturation']), step=0.05)
        width_boost = st.slider('Stereo Expansion', 1.0, 1.5, value=float(pv['width']), step=0.05)
        
    shimmer_amount = st.slider('ApeMachine Anti-Shimmer Intensity', 0.0, 1.0, value=float(pv['shimmer']), step=0.05)
# =====================================================================

    if st.button('PROCESS AND AUDITION CHANGES'):
        pb = st.progress(0)
        st_txt = st.empty()
        
        st_txt.text('Step 1: Stripping selective ID3 tags (TIT2, TPE1, COMM)...')
        pb.progress(25)
        st.session_state.purifier.strip()
        time.sleep(0.1)
        
        pb.progress(50)
        st_txt.text('Step 2: Processing Matrix FFT calculations...')
        
        with st.status("🔮 Step 2: Executing Matrix Engine...", expanded=True) as status_box:
            def update_status(msg, state):
                status_box.update(label=msg, state=state, expanded=(state == "running"))
                
            st.session_state.clean_bytes, st.session_state.lg, _ = st.session_state.purifier.purify_with_gate(
                threshold, saturation, width_boost, target_lufs, shimmer_amount, status_callback=update_status
            )
        
        st_txt.text('Step 3: Re-injecting intact BPM, Key & DAW Grid...')
        pb.progress(75)
        time.sleep(0.1)
        
        pb.progress(100)
        st.session_state.purifier.scan() # Scan opnieuw om UI te updaten
        st_txt.success('Audio successfully processed! Preview updated below.')

# --- RESULTATEN & AUDIO PREVIEW ---
if 'clean_bytes' in st.session_state and st.session_state.clean_bytes:
    st.markdown('### 🎧 Real-Time Audio Preview & Waveform Analysis')
    st.markdown('<div class="audio-player-box">', unsafe_allow_html=True)
    
    orig = st.session_state.purifier.orig_data[:, 0]
    sr = st.session_state.purifier.sr
    total_duration = len(orig) / sr
    
    v_col1, v_col2 = st.columns(2)
    with v_col1:
        zoom_window = st.slider('Zoom Window Size (Seconds)', 0.1, min(10.0, total_duration), value=min(2.0, total_duration), step=0.1, key='result_zoom_slider')
    with v_col2:
        start_time = st.slider('Timeline Position (Seconds)', 0.0, max(0.0, total_duration - zoom_window), value=0.0, step=0.1, key='result_timeline_slider')
        
    st.audio(st.session_state.clean_bytes, format='audio/wav', start_time=int(start_time))
    
    start_idx = int(start_time * sr)
    end_idx = int((start_time + zoom_window) * sr)
    st.line_chart(orig[start_idx:end_idx][::max(1, len(orig[start_idx:end_idx]) // 1000)])
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('### 📄 Processing Logs')
    st.markdown(f'<div class="log-box">{"<br>".join(st.session_state.lg)}</div>', unsafe_allow_html=True)
    
    base_name, _ = os.path.splitext(st.session_state.current_file)
    st.markdown('### 💾 Final Master Export')
    st.download_button(
        label='Download Purified Lossless WAV', 
        data=st.session_state.clean_bytes, 
        file_name=f'purified_{base_name}.wav', 
        mime='audio/wav',
        key='btn_final_audio_export'
    )

st.markdown('---')
st.markdown('### 🧹 Storage Management')
t_files = glob.glob(os.path.join(CACHE_DIR, '*'))
f_count = len(t_files)
f_size_mb = sum(os.path.getsize(f) for f in t_files) / (1024 * 1024) if f_count > 0 else 0.0
st.write(f'Generated Temp Files in .cache: **{f_count}** ({f_size_mb:.2f} MB)')

if st.button('Delete all generated files'):
    for f in t_files:
        try: os.remove(f)
        except: pass
    st.success('All temporary cache files successfully deleted!')
    time.sleep(0.5)
    st.rerun()
