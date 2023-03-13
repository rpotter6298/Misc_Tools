import time
import cv2
from pathlib import Path
from multiprocessing import Process, Queue
from playsound import playsound

sound_file = Path("C:/Ryan/misc_tools/webcam_monitor/ding.mp3")


def play_sound(sound_file, request_queue):
    # Check if the sound file exists
    if not sound_file.exists():
        print(f"Error: File not found: {sound_file}")
        return

    # Initialize last played time to 0
    last_played_time = 0

    # Keep listening for requests to play sounds
    while True:
        sound_request = request_queue.get()
        if sound_request:
            # Check if enough time has passed since the last played sound
            if (
                time.monotonic() - last_played_time > 10
            ):  # Play sound only if elapsed time is greater than 10 seconds
                # Play the requested sound file
                playsound(str(sound_file))
                # Update the last played time
                last_played_time = time.monotonic()


def detect_motion(sound_request_queue, prev_frame, cur_frame):
    # Convert frames to grayscale
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    cur_gray = cv2.cvtColor(cur_frame, cv2.COLOR_BGR2GRAY)

    # Compute the absolute difference between the current frame and the previous frame
    frame_diff = cv2.absdiff(cur_gray, prev_gray)

    # Apply thresholding to the difference frame to remove noise
    thresh = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)[1]

    # Find contours in the thresholded frame
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Check if any contour is big enough to be considered as motion
    for contour in contours:
        if cv2.contourArea(contour) > 5000:
            # Send a request to play the sound file
            sound_request_queue.put(True)
            return True

    # No motion detected
    return False


if __name__ == "__main__":
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Use DirectShow API
    # Create a queue to communicate with the sound playing process
    sound_request_queue = Queue()

    # Start the sound playing process as a daemon
    # sound_file = Path("ding.mp3")

    sound_process = Process(target=play_sound, args=(sound_file, sound_request_queue))
    sound_process.daemon = True
    sound_process.start()

    # Initialize previous frame to None
    prev_frame = None

    while True:
        # Capture frame-by-frame
        ret, cur_frame = cap.read()

        # Check if frame is successfully captured
        if not ret:
            break

        # Resize the frame to 640x480
        cur_frame = cv2.resize(cur_frame, (640, 480))

        # Flip the frame horizontally for a mirror effect
        cur_frame = cv2.flip(cur_frame, 1)

        # Convert frame to grayscale
        cur_gray = cv2.cvtColor(cur_frame, cv2.COLOR_BGR2GRAY)

        # Check if previous frame is not None
        if prev_frame is not None:
            # Detect motion in the current frame
            if detect_motion(sound_request_queue, prev_frame, cur_frame):
                cv2.putText(
                    cur_frame,
                    "Motion Detected",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2,
                )

        # Display the resulting frame
        cv2.imshow("Motion Detector", cur_frame)

        # Set current frame as previous frame
        prev_frame = cur_frame.copy()

        # Exit loop when the user presses the 'q' key
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Release the capture and destroy all windows
    cap.release()
    cv2.destroyAllWindows()
