import cv2
import time
import base64
import requests
from ultralytics import YOLO

# Client-specific configurations
CLIENT_ID = "1"  # Unique client identifier
SERVER_URL = "http://127.0.0.1:5000"  # Hub server URL
CAPTURE_INTERVAL = 10  # Interval between captures in seconds

# Load the YOLO model
model = YOLO("red_best.pt")  # Path to your custom YOLO model

# Global variables
threshold_value = None  # Threshold value initialized as None
COUNTER = 5  # Initial counter value


def fetch_command():
    """Fetch the command from the server."""
    try:
        response = requests.get(f"{SERVER_URL}/get_capture_status/{CLIENT_ID}")
        if response.status_code == 200:
            return response.json().get("command", "stop")
        print(f"Warning: Server returned status {response.status_code}.")
    except Exception as e:
        print(f"Error fetching command: {e}")
    return "stop"


def fetch_threshold():
    """Fetch the threshold value from the server."""
    global threshold_value
    try:
        response = requests.get(f"{SERVER_URL}/get_threshold/{CLIENT_ID}")
        if response.status_code == 200:
            threshold_value = response.json().get("threshold", None)
            print(f"{CLIENT_ID}: Fetched threshold is {threshold_value}.")
        else:
            print(f"Warning: Failed to fetch threshold. Status {response.status_code}")
    except Exception as e:
        print(f"Error fetching threshold: {e}")


def send_image_to_server(image_data, message):
    """Send image data to the server."""
    try:
        response = requests.post(
            f"{SERVER_URL}/receive_alert/{CLIENT_ID}",
            json={"image": image_data, "message": message},
        )
        if response.status_code == 200:
            print(f"Server response: {response.json()}")
        else:
            print(f"Warning: Failed to send image. Status {response.status_code}")
    except Exception as e:
        print(f"Error sending image: {e}")


def count_objects_in_frame(frame):
    """Process the image using the YOLO model and count the number of detected objects."""
    results = model(frame)  # Run the YOLO model on the frame
    return len(results[0].boxes), results  # Return the count and results


def capture_images():
    """Capture images based on the command."""
    global COUNTER  # Use global variables
    cap = None  # Initialize capture object
    print(f"{CLIENT_ID}: Starting image capture process...")

    while True:
        command = fetch_command()

        if command == "start":
            if cap is None:  # Open the camera only if not already opened
                cap = cv2.VideoCapture(0)
                if not cap.isOpened():
                    print(f"Error: Unable to access the camera on {CLIENT_ID}.")
                    break
                print(f"{CLIENT_ID}: Camera started.")

            fetch_threshold()  # Fetch the threshold value

            if threshold_value is None:
                print(f"{CLIENT_ID}: Threshold not set. Waiting for valid value...")
                time.sleep(1)
                continue

            ret, frame = cap.read()
            if ret:
                # Count objects in the current frame and get detection results
                object_count, results = count_objects_in_frame(frame)
                print(f"{CLIENT_ID}: Detected objects: {object_count}")

                # Display the detection results in a separate window
                for result in results:
                    plotted_frame = result.plot()
                    cv2.imshow("YOLO Detection", plotted_frame)

                # Break the loop if 'q' is pressed
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print(f"{CLIENT_ID}: Quitting the detection window.")
                    break

                # Compare the object count with the fetched threshold
                if object_count < threshold_value:
                    COUNTER -= 1
                    print(f"{CLIENT_ID}: Object count: {object_count} < Threshold count: {threshold_value} Counter: {COUNTER}")

                    if COUNTER == 0:
                        print(f"{CLIENT_ID}: Counter reached 0. Sending alert...")
                        # Encode the image to Base64
                        _, img_encoded = cv2.imencode(".jpg", frame)
                        img_data = base64.b64encode(img_encoded).decode("utf-8")
                        message = f"Object count below threshold detected by {CLIENT_ID}!"
                        send_image_to_server(img_data, message)
                        COUNTER = 5  # Reset the counter after sending the alert
                else:
                    print(f"{CLIENT_ID}: Object count: {object_count} < Threshold count: {threshold_value} Counter: {COUNTER}")
                    COUNTER = 5  # Reset the counter if threshold is met
            else:
                print(f"{CLIENT_ID}: Error capturing image.")

            time.sleep(CAPTURE_INTERVAL)  # Adjust the capture interval

        elif command == "stop":
            if cap is not None:  # Release the camera when stopping
                cap.release()
                cap = None
                print(f"{CLIENT_ID}: Camera stopped and released.")
            time.sleep(CAPTURE_INTERVAL)  # Wait before checking the status again

        else:
            print(f"{CLIENT_ID}: Unknown command '{command}'. Defaulting to stop.")
            time.sleep(CAPTURE_INTERVAL)

    # Cleanup on exit
    if cap is not None:
        cap.release()
        print(f"{CLIENT_ID}: Camera released on exit.")
    cv2.destroyAllWindows()


if __name__ == "__main__":
    capture_images()