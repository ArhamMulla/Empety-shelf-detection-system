# import cv2
# import time
# import base64
# import requests

# # Client-specific configurations
# CLIENT_ID = "1"  # Unique client identifier
# SERVER_URL = "http://127.0.0.1:5000"  # Hub server URL
# # SERVER_URL = "https://final-year-9my3.onrender.com"  # Hub server URL
# CAPTURE_INTERVAL = 10  # Interval between captures in seconds

# def fetch_command():
#     """Fetch the command from the server."""
#     try:
#         response = requests.get(f"{SERVER_URL}/get_capture_status/{CLIENT_ID}")
#         if response.status_code == 200:
#             return response.json().get("command", "stop")
#         print(f"Warning: Server returned status {response.status_code}.")
#     except Exception as e:
#         print(f"Error fetching command: {e}")
#     return "stop"

# def send_image_to_server(image_data, message):
#     """Send image data to the server."""
#     try:
#         response = requests.post(
#             f"{SERVER_URL}/receive_alert/{CLIENT_ID}",
#             json={"image": image_data, "message": message},
#         )
#         if response.status_code == 200:
#             print(f"Server response: {response.json()}")
#         else:
#             print(f"Warning: Failed to send image. Status {response.status_code}")
#     except Exception as e:
#         print(f"Error sending image: {e}")

# def capture_images():
#     """Capture images based on the command."""
#     cap = None  # Initialize capture object
#     print(f"{CLIENT_ID}: Starting image capture process...")

#     while True:
#         command = fetch_command()

#         if command == "start":
#             if cap is None:  # Open the camera only if not already opened
#                 cap = cv2.VideoCapture(0)
#                 if not cap.isOpened():
#                     print(f"Error: Unable to access the camera on {CLIENT_ID}.")
#                     break
#                 print(f"{CLIENT_ID}: Camera started.")

#             ret, frame = cap.read()
#             if ret:
#                 # Encode the captured image to Base64
#                 _, img_encoded = cv2.imencode(".jpg", frame)
#                 img_data = base64.b64encode(img_encoded).decode("utf-8")
#                 message = f"Empty space detected by {CLIENT_ID}"  # Customize the message
#                 send_image_to_server(img_data, message)
#             else:
#                 print(f"{CLIENT_ID}: Error capturing image.")

#             time.sleep(CAPTURE_INTERVAL)  # Adjust the capture interval

#         elif command == "stop":
#             if cap is not None:  # Release the camera when stopping
#                 cap.release()
#                 cap = None
#                 print(f"{CLIENT_ID}: Camera stopped and released.")
#             time.sleep(CAPTURE_INTERVAL)  # Wait before checking the status again

#         else:
#             print(f"{CLIENT_ID}: Unknown command '{command}'. Defaulting to stop.")
#             time.sleep(CAPTURE_INTERVAL)

#     # Cleanup on exit
#     if cap is not None:
#         cap.release()
#         print(f"{CLIENT_ID}: Camera released on exit.")
#     cv2.destroyAllWindows()

# if __name__ == "__main__":
#     capture_images()


import cv2
import time
import base64
import requests

# Client-specific configurations
CLIENT_ID = "1"  # Unique client identifier
SERVER_URL = "http://127.0.0.1:5000"  # Hub server URL
CAPTURE_INTERVAL = 10  # Interval between captures in seconds

threshold_value = None  # Threshold value initialized as None

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
            print(f"Threshold is: {threshold_value}")
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

def capture_images():
    """Capture images based on the command."""
    cap = None  # Initialize capture object
    print(f"{CLIENT_ID}: Starting image capture process...")

    while True:
        command = fetch_command()
        # print(command, "this is me")

        if command == "start":
            if cap is None:  # Open the camera only if not already opened
                cap = cv2.VideoCapture(0)
                if not cap.isOpened():
                    print(f"Error: Unable to access the camera on {CLIENT_ID}.")
                    break
                print(f"{CLIENT_ID}: Camera started.")

            fetch_threshold()  # Fetch the latest threshold

            ret, frame = cap.read()
            if ret:
                # Apply thresholding logic here using the threshold_value

                timestamp = int(time.time())
                _, buffer = cv2.imencode('.jpg', frame)
                image_data = base64.b64encode(buffer).decode('utf-8')
                message = f"Empty space detected at {time.ctime(timestamp)}"
                send_image_to_server(image_data, message)

                time.sleep(CAPTURE_INTERVAL)  # Wait for the next capture
            else:
                print(f"Error: Unable to capture image on {CLIENT_ID}.")

        elif command == "stop":
            if cap is not None:
                cap.release()
                cap = None
                print(f"{CLIENT_ID}: Camera stopped.")

        time.sleep(1)  # Check command periodically

if __name__ == "__main__":
    capture_images()