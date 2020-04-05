import os
import cv2
import numpy as np
import subprocess
import threading
import time

class AdbClass():
	_uniqueInstance = None
	LOCK = threading.Lock()

	POST_DELAY_TIME = 0.050

	@classmethod
	def __internal_new__(cls):
		return super().__new__(cls)
	
	@classmethod
	def getInstance(cls):
		if not cls._uniqueInstance:
			with AdbClass.LOCK:
				if not cls._uniqueInstance:
					cls._uniqueInstance = cls()
		return cls._uniqueInstance

	def screenCapRaw(self):
		self.rawImg = None
		try:
			self.rawImg = subprocess.check_output(['adb', 'exec-out', 'screencap'])
		except:
			self.rawImg = None

	def screenCapCv2(self, imgScale = 0.25, saveFlag=False, savePath='R:/screen.png'):
		print('screenCapCv2 start')
		# result = []
		# try:
		# 	with AdbClass.LOCK:
		# 		result = subprocess.check_output(['adb', 'exec-out', 'screencap'])
		# except:
		# 	return None
		self.rawImg = None
		proc = threading.Thread(target=self.screenCapRaw)
		with AdbClass.LOCK:
			proc.start()
			proc.join(10)
		
		if(None == self.rawImg):
			print('make dummy Image!!')
			img2 = np.zeros((720,360,3),np.uint8)
			return img2
		else:
			result = self.rawImg
			self.rawImg = None
		
		print('conv Image start')
		width = int.from_bytes(result[0:4], 'little')
		height = int.from_bytes(result[4:8], 'little')
		#_ = int.from_bytes(result[8:12], 'little')
		tmp = np.frombuffer(result[16:], np.uint8, -1, 0).copy() 
		img = np.reshape(tmp, (height, width, 4))    
		b = img[:, :, 0].copy()	# ここのコピーも必須
		img[:, :, 0] = img[:, :, 2]
		img[:, :, 2] = b
		img2 = np.delete(img, 3, 2)

		if(1.0 != imgScale):
			width = int(width * imgScale)
			height = int(height * imgScale)
			img2 = cv2.resize(img2, (width, height))
		
		if(saveFlag):
			cv2.imwrite(savePath, img2)
		
		print('screenCapCv2 end')
		return img2

	def tap(self, pos, loopCount=1):
		cmd = ['adb', 'shell', 'input', 'tap', str(pos[0]), str(pos[1])]
		with AdbClass.LOCK:
			for count in range(loopCount):
				subprocess.call(cmd)
			time.sleep(AdbClass.POST_DELAY_TIME)


	def swipe(self, startPos, endPos, loopCount=1):
		cmd = ['adb', 'shell', 'input', 'swipe', str(startPos[0]), str(startPos[1]), str(endPos[0]), str(endPos[1])]
		with AdbClass.LOCK:
			for count in range(loopCount):
				subprocess.call(cmd)
			time.sleep(AdbClass.POST_DELAY_TIME)

	def runCmdNoEcho(self, cmd, loopCount=1):
		with AdbClass.LOCK:
			for count in range(loopCount):
				subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			time.sleep(AdbClass.POST_DELAY_TIME)

if __name__ == '__main__':
	AdbClass.getInstance().screenCapCv2(saveFlag=True)
	#AdbClass.getInstance().tap((720,1800),10)
