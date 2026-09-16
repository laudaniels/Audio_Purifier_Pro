\# 🎛️ Audio Purifier Pro



Audio Purifier Pro is a powerful Streamlit application designed for \*\*Dynamic Spectral Gating \& Waveform Analysis\*\*.

It allows users to clean audio stems and strip intrusive AI-tracking or distribution metadata while keeping crucial musical properties—such as BPM and Key data—completely intact.



\---



\## 📸 Interface Preview



\### Intro Screen (Dashboard Launch)

\_Below is the initial landing page before uploading your audio stems:\_



<!-- PLACEHOLDER: INTRO\\\_SCREEN\\\_SCREENSHOT -->

!\[Audio Purifier Pro - Intro Screen](https://unsplash.com)

<!-- /PLACEHOLDER -->



\---



\## 🚀 Key Features



\- \*\*Selective ID3/RIFF Purification:\*\* Automatically strips restrictive tracking headers (`c2pa`, `TC260`) and specific ID3 tags (`TIT2` Title, `TPE1` Artist, `COMM` Comment) to neutralize AI footprinting.

\- \*\*Metadata Retention:\*\* Preserves critical musical elements like `acid` chunks (DAW grids), `TBPM` (BPM), and `TKEY` (Key) via an intelligent byte-injection system.

\- \*\*Advanced DSP Engine:\*\* Features a 2D Vectorized STFT Matrix Engine, Analog Tape Warmth (saturation), Stereo Field Expansion, and an ApeMachine Anti-Shimmer filter.

\- \*\*Real-Time Auditioning:\*\* In-app audio player linked directly to a downsampled waveform chart, enabling pinpoint zoom and precise timeline positioning.



\---



\### Analysis After Upload

\_Once a file is uploaded, the app performs a deep binary scan and visualizes which data is targeted and what stays secure:\_



<!-- PLACEHOLDER: ANALYSIS\\\_AFTER\\\_UPLOAD\\\_SCREENSHOT -->

!\[Audio Purifier Pro - Scan \& Analysis](https://unsplash.com)

<!-- /PLACEHOLDER -->



\---



\## 💻 Local Installation \& Setup



1\. \*\*Clone this repository\*\* to your local machine:

&#x20;  ```bash

&#x20;  git clone https://github.com

&#x20;  cd Audio\_Purifier\_Pro

&#x20;  ```



2\. \*\*Create and activate a virtual environment\*\* to keep dependencies isolated:

&#x20;  ```bash

&#x20;  python3 -m venv .venv

&#x20;  source .venv/bin/activate

&#x20;  ```



3\. \*\*Install the required packages\*\* using the requirements flag:

&#x20;  ```bash

&#x20;  pip install -r requirements.txt

&#x20;  ```



4\. \*\*Launch the application\*\*:

&#x20;  ```bash

&#x20;  streamlit run app.py

&#x20;  ```



\---



\### Processing Screen (DSP Engine Active)

\_The execution status box dynamically updates you on real-time FFT processing and final lossless WAV exports:\_



<!-- PLACEHOLDER: PROCESSING\\\_SCREEN\\\_SCREENSHOT -->

!\[Audio Purifier Pro - Processing \& Preview](https://unsplash.com)

<!-- /PLACEHOLDER -->



\---



\## 🛠️ Project Structure



```text

wav-stem-purifier-pro/

│

├── .cache/               (Temporarily generated files - hidden via .gitignore)

├── .gitignore            (Prevents heavy audio \\\& venv files from reaching GitHub)

├── README.md             (Project documentation)

├── requirements.txt      (Python dependencies)

├── app.py                (Streamlit UI \\\& layout handling)

├── core.py               (Signal processing \\\& selective binary injection)

└── styles.py             (Custom dark-themed CSS styling \\\& presets)

```

