# styles.py

PRESETS = {
    'Full Track': {'threshold': -45.0, 'saturation': 0.25, 'width': 1.15, 'lufs': -14.0, 'shimmer': 0.3},
    'Vocal Stem': {'threshold': -50.0, 'saturation': 0.40, 'width': 1.10, 'lufs': -12.0, 'shimmer': 0.7},
    'Drum Stem':  {'threshold': -35.0, 'saturation': 0.10, 'width': 1.30, 'lufs': -13.0, 'shimmer': 0.1},
    'Bass Stem':  {'threshold': -40.0, 'saturation': 0.20, 'width': 1.00, 'lufs': -14.0, 'shimmer': 0.0},
    'Other Stem': {'threshold': -45.0, 'saturation': 0.25, 'width': 1.20, 'lufs': -14.0, 'shimmer': 0.4}
}

CUSTOM_CSS = """
<style>
    .main { background-color: #0d0e15; color: #e2e8f0; }
    h1, h2, h3 { color: #a855f7; }
    .summary-box { background-color: #1a102f; border: 1px solid #a855f7; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
    .meta-content { background-color: #25183a; padding: 8px; border-radius: 4px; font-family: monospace; font-size: 11px; color: #e2e8f0; margin-top: 5px; word-break: break-all; }
    .log-box { background-color: #1e1b29; border-left: 4px solid #a855f7; padding: 15px; font-family: monospace; color: #38bdf8; margin-top: 15px; }
    .audio-player-box { background-color: #161424; padding: 15px; border-radius: 6px; margin-top: 15px; border: 1px solid #6366f1; }
    
    [data-testid='stFileUploader'] { padding: 30px; border: 2px dashed #6366f1; border-radius: 12px; background-color: #11101a; }
    [data-testid='stFileUploader'] section { padding: 40px !important; }
    [data-testid='stFileUploaderDropzone'] button { background-color: #a855f7 !important; padding: 10px 20px !important; color: white !important; }
    [data-testid='stMarkdownContainer'] p { font-size: 15px; }
</style>
"""
