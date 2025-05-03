import numpy as np
import streamlit as st
import time
import matplotlib
import matplotlib.pyplot as plt
from PIL import Image
import io
import base64

# Configure matplotlib to use 'Agg' backend
matplotlib.use('Agg')

# ===== CONSTANTS =====
GENRES = {
    0: 'Blues', 1: 'Classical', 2: 'Country',
    3: 'Disco', 4: 'Hip Hop', 5: 'Jazz',
    6: 'Metal', 7: 'Pop', 8: 'Reggae', 9: 'Rock'
}

COLOR_PALETTE = {
    'primary': '#6C5CE7',
    'secondary': '#00CEFF',
    'accent': '#FD79A8',
    'dark': '#0F0F1E',
    'light': '#F8F9FF',
    'success': '#00B894',
    'warning': '#FDCB6E',
    'danger': '#D63031'
}

# ===== ADVANCED CSS =====
st.markdown(f"""
<style>
/* Base Styles */
* {{
    font-family: 'Inter', sans-serif;
}}

.stApp {{
    background: linear-gradient(135deg, {COLOR_PALETTE['dark']}, #1A1A2E);
    color: white;
}}

/* Glassmorphism Components */
.glass-card {{
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-radius: 24px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    padding: 2rem;
    transition: all 0.3s ease;
}}

.glass-card:hover {{
    transform: translateY(-5px);
    box-shadow: 0 12px 40px rgba(108, 92, 231, 0.4);
}}

/* Animated Elements */
@keyframes float {{
    0% {{ transform: translateY(0px); }}
    50% {{ transform: translateY(-10px); }}
    100% {{ transform: translateY(0px); }}
}}

.music-note {{
    display: inline-block;
    font-size: 1.8rem;
    animation: float 3s ease-in-out infinite;
}}

/* Progress Bars */
.progress-container {{
    height: 8px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 4px;
    margin: 1rem 0;
    overflow: hidden;
}}

.progress-bar {{
    height: 100%;
    background: linear-gradient(90deg, {COLOR_PALETTE['primary']}, {COLOR_PALETTE['secondary']});
    border-radius: 4px;
    transition: width 0.5s ease;
}}

/* Custom File Uploader */
.stFileUploader > div {{
    border: 2px dashed {COLOR_PALETTE['accent']} !important;
    background: rgba(253, 121, 168, 0.05) !important;
    border-radius: 20px !important;
    transition: all 0.3s !important;
}}

.stFileUploader > div:hover {{
    border-color: {COLOR_PALETTE['secondary']} !important;
    background: rgba(0, 206, 255, 0.1) !important;
}}

/* Buttons */
.stButton > button {{
    background: linear-gradient(90deg, {COLOR_PALETTE['primary']}, {COLOR_PALETTE['secondary']}) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 2rem !important;
    font-weight: 600 !important;
    transition: all 0.3s !important;
    box-shadow: 0 4px 20px rgba(108, 92, 231, 0.3) !important;
}}

.stButton > button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 25px rgba(0, 206, 255, 0.4) !important;
    opacity: 0.9 !important;
}}

/* Visualization Containers */
.viz-container {{
    background: rgba(30, 30, 60, 0.6);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}}

/* Responsive Grid */
.grid-container {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
}}
</style>
""", unsafe_allow_html=True)

# ===== AUDIO VISUALIZATIONS =====
def generate_waveform():
    """Generate an animated waveform visualization"""
    x = np.linspace(0, 10, 100)
    y = np.sin(x * 3) * np.random.uniform(0.7, 1.3, 100)
    
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.plot(x, y, color=COLOR_PALETTE['secondary'], linewidth=2)
    ax.fill_between(x, y, color=COLOR_PALETTE['secondary'], alpha=0.2)
    ax.set_facecolor(COLOR_PALETTE['dark'])
    fig.patch.set_facecolor(COLOR_PALETTE['dark'])
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    return fig

def generate_spectrogram():
    """Generate a dynamic spectrogram visualization"""
    np.random.seed(int(time.time()))
    x = np.linspace(0, 10, 1000)
    y = np.sin(x * 5) * np.random.uniform(0.5, 1.5, 1000)
    
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.specgram(y, Fs=100, cmap='magma', aspect='auto')
    ax.set_facecolor(COLOR_PALETTE['dark'])
    fig.patch.set_facecolor(COLOR_PALETTE['dark'])
    ax.set_xlabel('Time', color='white')
    ax.set_ylabel('Frequency', color='white')
    ax.tick_params(colors='white')
    
    return fig

# ===== UI COMPONENTS =====
def genre_result_card(genre, confidence):
    """Create a genre result card with progress bar"""
    color = COLOR_PALETTE['primary'] if confidence > 85 else COLOR_PALETTE['accent']
    return f"""
    <div class="glass-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <h2 style="margin: 0; color: {color};">{genre}</h2>
            <div style="background: {color}; padding: 0.5rem 1rem; border-radius: 12px;">
                <h3 style="margin: 0; color: white;">{confidence:.1f}%</h3>
            </div>
        </div>
        <div class="progress-container">
            <div class="progress-bar" style="width: {confidence}%"></div>
        </div>
        <p style="color: #aaa; margin: 0.5rem 0 0;">AI confidence score</p>
    </div>
    """

# ===== MAIN APP =====
def main():
    # ---- APP HEADER ----
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown("""
        <div style="text-align: center;">
            <div style="font-size: 4rem;">
                <span class="music-note" style="animation-delay: 0s;">🎵</span>
                <span class="music-note" style="animation-delay: 0.3s;">🎶</span>
                <span class="music-note" style="animation-delay: 0.6s;">🎧</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="margin-left: 1rem;">
            <h1 style="margin-bottom: 0.2rem;">MelodyMind AI</h1>
            <p style="color: #aaa; margin-top: 0;">Advanced Music Genre Classification</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")

    # ---- MAIN CONTENT ----
    tab_analyze, tab_demo = st.tabs(["🔍 Analyze Music", "🎵 Genre Explorer"])

    with tab_analyze:
        st.markdown("""
        <div class="glass-card" style="margin-bottom: 2rem;">
            <h2 style="margin-top: 0;">Upload Your Music</h2>
            <p style="color: #aaa;">Discover the genre of any song with our AI-powered analysis</p>
        </div>
        """, unsafe_allow_html=True)

        uploaded_file = st.file_uploader("", type=["wav", "mp3"], label_visibility="collapsed")

        if uploaded_file:
            st.audio(uploaded_file)
            
            if st.button("Analyze Audio", type="primary", use_container_width=True):
                with st.spinner("Processing audio features..."):
                    # Simulate analysis progress
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for percent in range(0, 101, 5):
                        time.sleep(0.05)
                        progress_bar.progress(percent)
                        status_text.text(f"Analysis progress: {percent}%")
                    
                    # Generate random results for demo
                    random_genre = np.random.choice(list(GENRES.values()))
                    confidence = np.random.uniform(75, 97)
                    
                    progress_bar.empty()
                    status_text.empty()
                    
                    # Show results
                    st.markdown(genre_result_card(random_genre, confidence), unsafe_allow_html=True)
                    
                    # Visualizations
                    with st.expander("Advanced Audio Analysis", expanded=True):
                        st.markdown("""
                        <div class="viz-container">
                            <h3 style="margin-top: 0;">Waveform Analysis</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        st.pyplot(generate_waveform())
                        
                        st.markdown("""
                        <div class="viz-container">
                            <h3 style="margin-top: 0;">Frequency Spectrum</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        st.pyplot(generate_spectrogram())

    with tab_demo:
        st.markdown("""
        <div class="glass-card" style="margin-bottom: 2rem;">
            <h2 style="margin-top: 0;">Genre Characteristics</h2>
            <p style="color: #aaa;">Explore the unique features of different music genres</p>
        </div>
        """, unsafe_allow_html=True)
        
        selected_genre = st.selectbox("Select a genre", list(GENRES.values()))
        
        if st.button("Show Analysis", key="analyze_genre", use_container_width=True):
            with st.spinner(f"Analyzing {selected_genre} patterns..."):
                time.sleep(1.5)
                
                st.markdown(f"""
                <div class="glass-card">
                    <h2 style="margin-top: 0;">{selected_genre} Features</h2>
                </div>
                """, unsafe_allow_html=True)
                
                # Feature visualization
                features = {
                    "Energy": np.random.uniform(0.7, 0.95),
                    "Danceability": np.random.uniform(0.5, 0.9),
                    "Tempo": np.random.randint(80, 160),
                    "Acousticness": np.random.uniform(0.1, 0.8),
                    "Valence": np.random.uniform(0.3, 0.9)
                }
                
                cols = st.columns(2)
                with cols[0]:
                    st.markdown("#### Audio Characteristics")
                    for feature, value in features.items():
                        if feature == "Tempo":
                            st.markdown(f"""
                            <div style="margin-bottom: 1rem;">
                                <div style="display: flex; justify-content: space-between;">
                                    <span>{feature}</span>
                                    <span>{value} BPM</span>
                                </div>
                                <div class="progress-container">
                                    <div class="progress-bar" style="width: {(value/200)*100}%"></div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div style="margin-bottom: 1rem;">
                                <div style="display: flex; justify-content: space-between;">
                                    <span>{feature}</span>
                                    <span>{value:.0%}</span>
                                </div>
                                <div class="progress-container">
                                    <div class="progress-bar" style="width: {value*100}%"></div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                
                with cols[1]:
                    st.markdown("#### Genre Similarity")
                    similar_genres = np.random.choice(
                        [g for g in GENRES.values() if g != selected_genre],
                        size=3,
                        replace=False
                    )
                    
                    for genre in similar_genres:
                        similarity = np.random.uniform(60, 85)
                        st.markdown(f"""
                        <div style="margin-bottom: 1rem;">
                            <div style="display: flex; justify-content: space-between;">
                                <span>{genre}</span>
                                <span>{similarity:.0f}%</span>
                            </div>
                            <div class="progress-container">
                                <div class="progress-bar" style="width: {similarity}%; background: {COLOR_PALETTE['secondary']}"></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

    # ---- SIDEBAR ----
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h2>MelodyMind</h2>
            <div style="height: 3px; background: linear-gradient(to right, {COLOR_PALETTE['primary']}, {COLOR_PALETTE['secondary']}); border-radius: 3px; margin: 0.5rem 0;"></div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="glass-card" style="margin-bottom: 2rem;">
            <h4 style="margin-top: 0;">How It Works</h4>
            <p style="font-size: 0.9rem; color: #aaa;">
                Our AI analyzes the acoustic fingerprint of your music including:
                <ul style="color: #aaa; font-size: 0.9rem;">
                    <li>Melodic patterns</li>
                    <li>Rhythmic structures</li>
                    <li>Harmonic content</li>
                    <li>Spectral features</li>
                </ul>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="glass-card">
            <h4 style="margin-top: 0;">Supported Genres</h4>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.5rem;">
        """ + 
        "".join([f"""
        <div style="display: flex; align-items: center;">
            <div style="width: 8px; height: 8px; background: {COLOR_PALETTE['accent']}; border-radius: 50%; margin-right: 8px;"></div>
            <span style="font-size: 0.9rem;">{genre}</span>
        </div>
        """ for genre in GENRES.values()]) +
        """
            </div>
        </div>
        """, unsafe_allow_html=True)

if __name__ == '__main__':
    main() 

    