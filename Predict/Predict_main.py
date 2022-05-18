import cv2
from PIL import Image
import numpy as np

try:
	from Predict.keras_yolo3.yolo import YOLO
	from Predict.handleTime import Time
except ImportError:
	from keras_yolo3.yolo import YOLO
	from handleTime import Time

BASERUNTIME = [0,14,0,0]

"""

model:

Loads YOLO model with config "data"

model_config:
	model_path:
		Path to the model
		Ex: '../LastModel_yv3/yolov3_15102020_final.h5'
	anchors_path:
		Path to the file contains anchors
		Ex: './FilesToPred/yolo_anchors.txt'
	classes_path:
		Path to the file contains classes of our model
		Ex: './FilesToPred/data_classes.txt'
	score:
		Minimum score above the model will shows predicted data
		Ex: 0.5
	model_image_size:
		Size of the input image of the model
		Ex: (416, 416)

class Predictor:

Prediction loop, it will open video and pass each frame of the video as model input
The model will output predictions on the frame
After each prediction, the results will be saved with class contained in variable: expy_pred
At the end of the video the model session will be closed and the scripts quits

To show real-time predictions on the video you must set the flag : show_video to True
When the model is running in show video mode, you can exit pressing "q" key.

"""

def model(data):
	return YOLO(**data)

class Predictor:
	def __init__(self, model, path):
		self.model = model
		self.path = path
		self._load()

	def _load(self,):
		self.vid = cv2.VideoCapture(self.path)
		if not self.vid.isOpened():
			raise IOError("Couldn't open webcam or video")
		fps = self.vid.get(cv2.CAP_PROP_FPS)
		frame_count = int(self.vid.get(cv2.CAP_PROP_FRAME_COUNT))
		self.t = Time(fps, frame_count, BASERUNTIME, cheat=True)

	def run(self, expy_pred=None, show_video=False):
		it_time = 0
		while self.vid.isOpened():
			fdata, frame = self.vid.read()
			if not fdata:
				break
			frame = frame[:, :, ::-1]
			image = Image.fromarray(frame)
			out_pred, image = self.model.detect_image(
				image,
				show_stats=False)
			cur_time = self.t.up(it_time)
			print(out_pred)
			if expy_pred != None:
				expy_pred.run(out_pred, cur_time)
			if show_video:
				result = np.asarray(image)
				cv2.namedWindow("VIDEO", cv2.WINDOW_NORMAL)
				cv2.imshow("VIDEO", result)
				if cv2.waitKey(1) & 0xFF == ord('q'):
					break
			it_time+=1
		self.vid.release()


def main():
	m_model = model({
		"model_path": '../LastModel_yv3/yolov3_15102020_final.h5',
		"anchors_path": '../Config/FilesToPred/yolo_anchors.txt',
		"classes_path": '../Config/FilesToPred/data_classes.txt',
		"score": 0.5,
		"gpu_num": 1,
		"model_image_size": (416, 416),
	})
	Predictor(m_model, '../Data/ExportH45Cut.mp4').run(show_video=True)
	m_model.close_session()

if __name__ == "__main__":
	main()