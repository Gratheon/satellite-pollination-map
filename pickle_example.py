import pickle
import numpy as np
from PIL import Image
import torch
import torchvision.transforms as transforms

# Load the model from the pickle file
with open('classifier_model.pkl', 'rb') as file:
    model = pickle.load(file)

def inference():

    # Load and preprocess the image
    image_path = 'your_image.png'  # Replace with your image file
    image = Image.open(image_path)
    transform = transforms.Compose([
        transforms.Resize((512, 512)),
        transforms.ToTensor(),
        # Add any other necessary preprocessing steps here
    ])
    image = transform(image)
    image = image.unsqueeze(0)  # Add a batch dimension

    # Perform inference on the CPU
    with torch.no_grad():
        output = model(image)
