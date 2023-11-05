
import argparse
import pickle
import rasterio
from rasterio.plot import reshape_as_image
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
import joblib


model_path= Path('classifier.pkl')
classified_path= Path('Results/classification_request.tif')

class Classificator:
    def __init__(self, args=None):
        self.filename=None
        self.parseargs(args)
        self.image_profile= None
    
    def parseargs(self, args):
        if args is None:
            return
        if "filename" in args:
            self.filename = Path(args["filename"])
            print('success parsing args!! ', self.filename)

    def execute(self):
        dataset = rasterio.open(self.filename)
        self.image_profile= dataset.profile
        image= dataset.read()
        reshaped_img = reshape_as_image(image)
        img_shape= reshaped_img[:,:,0].shape
        #model= pickle.load(open(model_path, 'rb'))
        model= joblib.load(model_path)
        prediction= model.predict(self.filename)
        self.save_as_image(prediction, img_shape)
        
    def save_as_image(self, prediction, shape):
        image = prediction.reshape(shape)
        profile = self.image_profile
        profile.update(dtype=rasterio.uint8,count=1, compress='lzw')
        # change the band count to 1, set the dtype to uint8, and specify LZW compression.
        profile.update(dtype=rasterio.uint8,count=1, compress='lzw')
        with rasterio.open(classified_path, 'w', **profile) as dst:
            dst.write(image.astype(rasterio.uint8),1)
        return image
    
if __name__ == "__main__":
    arguments= argparse.ArgumentParser()
    arguments.add_argument("-f", "--filename", help="Input filename")
    args = vars(arguments.parse_args())
    extractor = Classificator(args)
    extractor.execute()