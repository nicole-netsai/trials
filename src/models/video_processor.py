import cv2
import os
import streamlit as st
from ultralytics import YOLO
from video_processing import process_frame, draw_parking_overlay
import io

@st.cache_resource(show_spinner="Loading parking detection model...")
def load_model():
    """Load the YOLO model for car detection"""
    try:
        model = YOLO('yolov8n.pt')
        return model
    except Exception as e:
        st.error(f"Model loading failed: {str(e)}")
        return None

def process_video(video_path, model, lot_id):
    """Process video to count cars and update parking lot status"""
    cap = cv2.VideoCapture(video_path)
    car_count = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        results = model(frame, verbose=False)
        for result in results:
            boxes = result.boxes
            car_count += len([box for box in boxes if box.cls == 2])
    
    cap.release()
    
    lot = next(lot for lot in st.session_state.parking_lots if lot["id"] == lot_id)
    lot["occupied"] = min(car_count, lot["capacity"])
    
    return car_count

def analyze_video_feed(uploaded_video):
    """Analyze uploaded video feed with pause, timestamp, and script download support"""
    if uploaded_video:
        model = load_model()
        temp_video = "temp_video.mp4"
        # Write the video to a temporary file if not already done
        if "video_processed" not in st.session_state or st.session_state.last_video_name != uploaded_video.name:
            with open(temp_video, "wb") as f:
                f.write(uploaded_video.getbuffer())
            st.session_state.video_processed = True
            st.session_state.last_video_name = uploaded_video.name

        # Initialize session state variables
        if "pause" not in st.session_state:
            st.session_state.pause = False
        if "frame_count" not in st.session_state:
            st.session_state.frame_count = 0
        if "space_status" not in st.session_state:
            st.session_state.space_status = {i: False for i in range(1, 13)}
        if "last_frame" not in st.session_state:
            st.session_state.last_frame = None

        # Create a function to toggle pause state
        def toggle_pause():
            st.session_state.pause = not st.session_state.pause

        st.button("Pause/Resume", on_click=toggle_pause)
        st_frame = st.empty()
        progress_bar = st.progress(0)
        paused_info = st.empty()
        download_btn = st.empty()

        cap = cv2.VideoCapture(temp_video)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        if not fps or fps == 0:
            st.warning("Could not determine video FPS. Using default value of 25.")
            fps = 25
        if total_frames == 0:
            st.error("Could not read any frames from the video. Please upload a valid video file.")
            cap.release()
            return

        # Defensive: Don't seek past end
        if st.session_state.frame_count >= total_frames:
            st.session_state.frame_count = 0

        # If paused, just show the last processed frame
        if st.session_state.pause:
            timestamp = f"{int(st.session_state.frame_count//fps):02d}:{int((st.session_state.frame_count%fps)*(60//fps)):02d}"
            space_status = st.session_state.space_status
            free_count = sum(1 for v in space_status.values() if not v)
            paused_info.info(f"Paused at {timestamp}")
            # Show the last processed frame and download as image
            if st.session_state.last_frame is not None:
                st_frame.image(st.session_state.last_frame, channels="BGR")
                progress_bar.progress(min(st.session_state.frame_count/total_frames, 1.0))
                is_success, buffer = cv2.imencode(".png", st.session_state.last_frame)
                if is_success:
                    img_bytes = io.BytesIO(buffer)
                    download_btn.download_button(
                        label="Download Current Frame",
                        data=img_bytes,
                        file_name=f"frame_{timestamp.replace(':','_')}.png",
                        mime="image/png"
                    )
            cap.release()
            return

        # Process video frames if not paused
        cap.set(cv2.CAP_PROP_POS_FRAMES, st.session_state.frame_count)
        try:
            while cap.isOpened() and not st.session_state.pause:
                ret, frame = cap.read()
                if not ret:
                    st.warning("End of video or failed to read frame. Resetting to start.")
                    st.session_state.frame_count = 0
                    break
                frame = cv2.resize(frame, (1020, 500))
                timestamp = f"{int(st.session_state.frame_count//fps):02d}:{int((st.session_state.frame_count%fps)*(60//fps)):02d}"
                space_status = process_frame(frame, model)
                st.session_state.space_status = space_status  # Save to session state
                annotated_frame = draw_parking_overlay(frame, space_status, timestamp=timestamp)
                st.session_state.last_frame = annotated_frame  # Save last frame
                st_frame.image(annotated_frame, channels="BGR")
                progress_bar.progress(min(st.session_state.frame_count/total_frames, 1.0))
                st.session_state.frame_count += 1
                # cv2.waitKey(1)  # REMOVED: Not needed in Streamlit
        finally:
            cap.release()
            if os.path.exists(temp_video) and "keep_temp_file" not in st.session_state:
                os.remove(temp_video)
        if st.session_state.frame_count >= total_frames:
            progress_bar.empty()
            st.success("Analysis complete!")