import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import re
from datetime import datetime
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="YouTube Summarizer Pro",
    page_icon="📝",
    layout="wide"
)

# Load environment variables and configure
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

@st.cache_data(ttl=3600)
def extract_video_id(youtube_url):
    try:
        if 'youtu.be' in youtube_url:
            return youtube_url.split('/')[-1].split('?')[0]
        video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', youtube_url)
        return video_id_match.group(1) if video_id_match else None
    except Exception as e:
        st.error(f"Error extracting video ID: {str(e)}")
        return None

@st.cache_data(ttl=3600)
def extract_video_metadata(video_id):
    try:
        import yt_dlp
        ydl = yt_dlp.YoutubeDL({'quiet': True})
        result = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
        return {
            'title': result.get('title', 'Unknown'),
            'channel': result.get('uploader', 'Unknown'),
            'duration': result.get('duration', 0),
            'views': result.get('view_count', 0)
        }
    except Exception as e:
        st.warning(f"Could not fetch video metadata: {str(e)}")
        return None

@st.cache_data(ttl=3600)
def extract_transcript_details(youtube_video_url):
    try:
        video_id = extract_video_id(youtube_video_url)
        if not video_id:
            return None, None
        
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
        
        formatted_transcript = []
        for item in transcript_data:
            start_time = int(item['start'])
            text = item['text']
            timestamp = f"{start_time // 60:02d}:{start_time % 60:02d}"
            formatted_transcript.append({'timestamp': timestamp, 'text': text})
        
        full_transcript = " ".join(item["text"] for item in transcript_data)
        return full_transcript, formatted_transcript
    
    except Exception as e:
        st.error(f"Error extracting transcript: {str(e)}")
        return None, None

def generate_gemini_content(transcript_text, prompt_template, summary_type="detailed"):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        if summary_type == "quick":
            prompt = f"""Provide a concise 2-3 sentence summary of the main points from this video transcript: {transcript_text}"""
        elif summary_type == "chapter":
            prompt = f"""Break this video transcript into logical chapters/sections with timestamps and brief descriptions: {transcript_text}"""
        else:
            prompt = prompt_template + transcript_text
            
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating summary: {str(e)}")
        return None

def save_summary(summary, video_id, metadata):
    try:
        df = pd.DataFrame({
            'timestamp': [datetime.now()],
            'video_id': [video_id],
            'title': [metadata.get('title', 'Unknown')],
            'summary': [summary]
        })
        
        filename = 'summaries_history.csv'
        if os.path.exists(filename):
            df.to_csv(filename, mode='a', header=False, index=False)
        else:
            df.to_csv(filename, index=False)
        return True
    except Exception as e:
        st.error(f"Error saving summary: {str(e)}")
        return False

# Streamlit UI
st.title("📝 YouTube Transcript to Detailed Notes Converter")
st.markdown("Transform any YouTube video into comprehensive notes with AI-powered summarization.")

# Sidebar settings
with st.sidebar:
    st.header("⚙️ Settings")
    summary_type = st.selectbox("Summary Type", ["detailed", "quick", "chapter"])
    save_to_file = st.checkbox("Save Summary to File", value=False)

# Main content
youtube_link = st.text_input("🔗 Enter YouTube Video Link:", placeholder="https://www.youtube.com/watch?v=...")

if youtube_link:
    video_id = extract_video_id(youtube_link)
    if video_id:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)
        
        with col2:
            metadata = extract_video_metadata(video_id)
            if metadata:
                st.markdown("### Video Details")
                st.write(f"📺 **Title:** {metadata['title']}")
                st.write(f"👤 **Channel:** {metadata['channel']}")
                st.write(f"⏱️ **Duration:** {metadata['duration'] // 60}:{metadata['duration'] % 60:02d} minutes")
                st.write(f"👁️ **Views:** {metadata['views']:,}")

if st.button("🚀 Generate Summary"):
    with st.spinner("🔄 Processing... This may take a few moments."):
        transcript_text, formatted_transcript = extract_transcript_details(youtube_link)
        
        if transcript_text:
            # Show transcript in expander
            with st.expander("📜 View Original Transcript"):
                transcript_df = pd.DataFrame(formatted_transcript)
                st.dataframe(transcript_df, use_container_width=True)
            
            # Generate and display summary
            summary = generate_gemini_content(
                transcript_text,
                prompt_template="""Provide a comprehensive summary of this video transcript, including:
                1. Main topics and key points
                2. Important details and examples
                3. Key takeaways
                Please format the summary in clear paragraphs with proper headings:\n\n""",
                summary_type=summary_type
            )
            
            if summary:
                st.markdown("### 📋 Summary")
                st.write(summary)
                
                if save_to_file and metadata:
                    if save_summary(summary, video_id, metadata):
                        st.success("✅ Summary saved successfully!")
                
                # Download buttons
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        "📥 Download Summary",
                        summary,
                        file_name=f"summary_{video_id}.txt",
                        mime="text/plain"
                    )
                with col2:
                    if formatted_transcript:
                        transcript_text = "\n".join([f"{item['timestamp']}: {item['text']}" for item in formatted_transcript])
                        st.download_button(
                            "📥 Download Transcript",
                            transcript_text,
                            file_name=f"transcript_{video_id}.txt",
                            mime="text/plain"
                        )

# Footer
st.markdown("---")
st.markdown("""
    <div class="footer">
        <p>Developed with ❤ by <a href="https://github.com/shlok025" target="_blank">Shlok Gaikwad</a></p>
        <p>⚡ Features: Transcription, Summarization, Chapter Detection, and Download Options</p>
    </div>
""", unsafe_allow_html=True)