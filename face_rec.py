import threading

import face_recognition
import cv2
import time
import nfc
from pymongo import MongoClient
import ndef


cluster = MongoClient("mongodb+srv://bernardorhyshunch:TakingInventoryIsFun@cluster0.jpb6w.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = cluster["Inventory"]
collection1 = db["astro"]
collection = db["Inventory"]
clf = nfc.ContactlessFrontend('usb')

class NFCReaderThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.result = None
        self.error = None

    def run(self):
        try:
            self.result = nfc_read()
        except Exception as e:
            self.error = e

def load_known_faces():
    known_faces = []
    try:
        # Load all reference faces
        for i in range(0, 6):
            img = face_recognition.load_image_file(f"pictures/face{i}.jpg")
            encoding = face_recognition.face_encodings(img)[0]
            known_faces.append(encoding)
        return known_faces
    except FileNotFoundError:
        print("Error: One or more face images not found in 'pictures' directory")
        exit(1)
    except IndexError:
        print("Error: No face detected in one or more reference images")
        exit(1)

def capture_and_compare(cap, known_faces):
    """Capture a frame and compare with known faces"""
    ret, frame = cap.read()
    if not ret:
        print("Error: Cannot read from webcam")
        return None

    try:
        # Get encoding of face in current frame
        current_face_encoding = face_recognition.face_encodings(frame)[0]
        print("current face encoding")
        # Compare with known faces
        results = face_recognition.compare_faces(known_faces, current_face_encoding)
        # Get indices of matching faces
        matches = [index for index, value in enumerate(results) if bool(value)]
        return matches

    except IndexError:
        print("No face detected in camera frame")
        return None

def idnumber(tag_data):
    if "NFCNASAMED" in str(tag_data):
        print("scanned" + str(tag_data))
        splitmeds = str(tag_data).split('%')
        intmeds = int(splitmeds[2])
        return intmeds

    else:
        print("med unknown tag")

def nfc_read():
    tag = clf.connect(rdwr={'on-connect': lambda tag: False})
    tag_data = tag.ndef.records
    if tag_data is None:
        print("no tag data")
        return

    id_num = idnumber(tag_data)
    if id_num is not None:
        collection.update_many({"_id": id_num}, {"$inc": {"Amount": -1}})
        return id_num

    if id_num is None:
        print("no id num data")
        return


def check_value_with_timeout(timeout_seconds):
    print("Waiting for NFC tag with timeout...")

    # Start NFCReaderThread, which runs nfc_read() in the background
    nfc_thread = NFCReaderThread()
    nfc_thread.start()  # Start running the thread
    nfc_thread.join(timeout_seconds)

    if nfc_thread.is_alive():
        print("NFC read timeout reached, stopping NFC read...")
        return None

    if nfc_thread.error:
        print(f"Error in NFC reader: {nfc_thread.error}")
        return None

    print(f"NFC Read Result: {nfc_thread.result}")
    return nfc_thread.result

def db_edit_face(matches, intmeds):

    idastro = int(matches[0])
    if idastro and intmeds is not None:
        collection1.update_many({"_id": idastro}, {"$inc": {f"Amount:{intmeds}": 1}})
        print(f"face matches with {idastro} :D ")
        return

    if idastro is None:
        print("no matching face data")
        return

def main():
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    print("webcam started")
    try:
        known_faces = load_known_faces()
        print("known faces loaded")
    except Exception as e:
        print(f"Error: {e}")
        print("Exiting...")
        return

    while True:
        if not cap.isOpened():
            print("Error: Cannot open webcam")
            return

        try:
            # Load known faces
            # Capture and process one frame
            matches = capture_and_compare(cap, known_faces)
            result = check_value_with_timeout(10)
            print(matches)
            if matches is not None:
                try:
                    if result is None:
                        print("no nfc tag scanned")
                        continue

                    if result is not None:
                        intmeds = nfc_read()
                        db_edit_face(matches, intmeds)
                        print("ready")
                    else:
                        print("AAAAAAAAAAAAAA")
                        continue
                except AttributeError:
                    print("no tag data")
            else:
                print("No matching face detected")
                time.sleep(2)
                print("ready")

        except KeyboardInterrupt:
            # Clean up
            cap.release()
            cv2.destroyAllWindows()
            clf.close()

if __name__ == "__main__":
    main()