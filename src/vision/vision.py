import numpy as np
from picamera2 import Picamera2
import cv2
from hailo_platform import (HEF, VDevice, HailoStreamInterface, InferVStreams, ConfigureParams,
    InputVStreamParams, OutputVStreamParams, FormatType)

import time

# Initialisation de la caméra avec picamera2
camera = Picamera2()
camera.configure(camera.create_preview_configuration(main={"size": (640, 640)}))
camera.start()

# Configuration du modèle YOLO
model_name = 'yolov5'
hef_path = '/usr/share/hailo-models/yolov8s_h8l.hef'.format(model_name)
hef = HEF(hef_path)

# Configuration du périphérique Hailo
target = VDevice()
configure_params = ConfigureParams.create_from_hef(hef=hef, interface=HailoStreamInterface.PCIe)
network_groups = target.configure(hef, configure_params)
network_group = network_groups[0]
network_group_params = network_group.create_params()

# Création des paramètres de flux virtuels d'entrée et de sortie
input_vstreams_params = InputVStreamParams.make(network_group, format_type=FormatType.UINT8)
output_vstreams_params = OutputVStreamParams.make(network_group, format_type=FormatType.FLOAT32)

# Récupération des informations sur les flux virtuels
input_vstream_info = hef.get_input_vstream_infos()[0]
output_vstream_info = hef.get_output_vstream_infos()[0]
image_height, image_width, channels = input_vstream_info.shape

print(f"Taille d'entrée du modèle: {image_width}x{image_height} avec {channels} canaux")


# Fonction pour prétraiter l'image
def preprocess_image(image):
    resized_image = cv2.resize(image, (image_width, image_height))
    if resized_image.shape[-1] == 4:
        resized_image = cv2.cvtColor(resized_image, cv2.COLOR_BGRA2BGR)
    #normalized_image = resized_image / 255.0
    normalized_image = resized_image.astype(np.uint8)
    print(f"Shape des données d'entrée : {normalized_image.shape}")

    return normalized_image
    #return normalized_image.astype(np.float32)

# Fonction pour post-traiter les résultats YOLO
def postprocess_results(results):
    # Supposons que les résultats soient sous forme de tableau avec les classes détectées
    detected_objects = []
    print("XXXXXXXXXX")
    print(results)
    print("XXXXXXXXXX")
    for result in results:
        try:
            class_id = np.argmax(result)
            detected_objects.append(class_id)
        except:
            pass
    return detected_objects

# Fonction principale pour la détection d'objets
def detect_objects():
    i = 0
    with InferVStreams(network_group, input_vstreams_params, output_vstreams_params) as infer_pipeline:
        with network_group.activate(network_group_params):
            while True:
                # Capture d'une image avec picamera2
                frame = camera.capture_array()

                # Prétraitement de l'image
                input_data = preprocess_image(frame)
                cv2.imshow('Frame', frame)
                input_data = np.expand_dims(input_data, axis=0)  # Ajout de la dimension batch

                # Inférence
                input_data = {input_vstream_info.name: input_data}
                infer_results = infer_pipeline.infer(input_data)
                results = infer_results[output_vstream_info.name]

                # Post-traitement des résultats
                detected_objects = postprocess_results(results)
                print("Objets détectés :", detected_objects)

                # Affichage de l'image avec les objets détectés
                for obj in detected_objects:
                    cv2.putText(frame, str(obj), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                #cv2.imshow('Détection d\'objets', frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
                i+=1

                if i > 2:
                    time.sleep(300)

    camera.stop()
    cv2.destroyAllWindows()
    target.release()

if __name__ == "__main__":
    detect_objects()



