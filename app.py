import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import re
from datetime import datetime
import pandas as pd
import textwrap

# Page configuration
st.set_page_config(
    page_title="YouTube Summarizer Pro",
    page_icon="📝",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .success-message {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        color: #155724;
        margin: 1rem 0;
    }
    .error-message {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        color: #721c24;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Load environment variables and configure
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY")) #Put your Google api Key here

# Cache the results to avoid repeated API calls
@st.cache_data(ttl=3600)  # Cache for 1 hour
def extract_video_id(youtube_url):
    """
    Extract video ID from different YouTube URL formats
    """
    try:
        video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', youtube_url)
        if video_id_match:
            return video_id_match.group(1)
        return None
    except Exception as e:
        st.error(f"Error extracting video ID: {str(e)}")
        return None

@st.cache_data(ttl=3600)
def extract_video_metadata(video_id):
    """
    Extract video metadata using YouTube API (requires youtube-dl library)
    """
    try:
        import yt_dlp
        ydl = yt_dlp.YoutubeDL({'quiet': True})
        result = ydl.extract_info(
            f"https://www.youtube.com/watch?v={video_id}",
            download=False
        )
        return {
            'title': result.get('title', 'Unknown'),
            'channel': result.get('uploader', 'Unknown'),
            'duration': result.get('duration', 0),
            'views': result.get('view_count', 0),
            'upload_date': result.get('upload_date', 'Unknown')
        }
    except Exception as e:
        st.warning(f"Could not fetch video metadata: {str(e)}")
        return None

@st.cache_data(ttl=3600)
def extract_transcript_details(youtube_video_url):
    """
    Extract transcript from YouTube video with language selection
    """
    try:
        video_id = extract_video_id(youtube_video_url)
        if not video_id:
            st.error("Could not extract video ID from URL")
            return None
        
        # Get available transcripts
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Try to get English transcript first, fall back to auto-generated
        try:
            transcript = transcript_list.find_transcript(['en'])
        except:
            try:
                transcript = transcript_list.find_generated_transcript(['en'])
            except:
                # Get the first available transcript
                transcript = transcript_list.find_generated_transcript(['en'])
        
        transcript_data = transcript.fetch()
        
        # Create formatted transcript with timestamps
        formatted_transcript = []
        for item in transcript_data:
            start_time = int(item['start'])
            text = item['text']
            minutes = start_time // 60
            seconds = start_time % 60
            timestamp = f"{minutes:02d}:{seconds:02d}"
            formatted_transcript.append({
                'timestamp': timestamp,
                'text': text
            })
        
        # Join for summary generation
        full_transcript = " ".join(item["text"] for item in transcript_data)
        
        return full_transcript, formatted_transcript
    
    except Exception as e:
        st.error(f"Error extracting transcript: {str(e)}")
        return None, None

def generate_gemini_content(transcript_text, prompt_template, summary_type="detailed"):
    """
    Generate summary using Gemini Pro with different summary types
    """
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        
        if summary_type == "quick":
            prompt = f"""Provide a concise 2-3 sentence summary of the main points from this video transcript: {transcript_text}"""
        elif summary_type == "chapter":
            prompt = f"""Break this video transcript into logical chapters/sections with timestamps and brief descriptions: {transcript_text}"""
        else:  # detailed
            prompt = prompt_template + transcript_text
            
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating summary: {str(e)}")
        return None

def save_summary(summary, video_id, metadata):
    """
    Save summary to CSV file
    """
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

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Settings")
    summary_type = st.selectbox(
        "Summary Type",
        ["detailed", "quick", "chapter"],
        help="Choose the type of summary you want to generate"
    )
    
    language_preference = st.selectbox(
        "Preferred Language",
        ["English", "Auto-detect"],
        help="Choose the preferred language for transcript"
    )
    
    show_timestamps = st.checkbox("Show Timestamps in Summary", value=True)
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
                
                # Save summary if requested
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