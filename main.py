import os
import cv2
import numpy as np
import time
import datetime
import threading
import subprocess
from pathlib import Path

from AdbClass import AdbClass

IMG_SCALE = 0.25

STATUS_INIT = 0
STATUS_STARTING = 1
STATUS_NORMAL = 2
STATUS_QUEST = 3
STATUS_ENDING = 9


class ScreenProcClass():
	def __init__(self, templatePath='./template'):
		path = Path(templatePath)
		templateFileList = list(path.glob('**/*.png'))
		self.templateImgList = {}
		for templateFile in templateFileList:
			baseName = templateFile.stem
			tempImg = cv2.imread(os.path.abspath(templateFile))

			# width = int(tempImg.shape[1] * IMG_SCALE)
			# height = int(tempImg.shape[0] * IMG_SCALE)
			# tempImg = cv2.resize(tempImg, (width, height))

			# self.templateImgList[baseName] = tempImg
			self.templateImgList[baseName] = self.resizeImage(tempImg, IMG_SCALE)

	def checkTemplate(self, srcImg, templateName):
		matchRes = False
		matchPos2 = (0, 0)
		outImg = srcImg.copy()
		tempImg = self.templateImgList[templateName]
		tempWidth = tempImg.shape[1]
		tempHeight = tempImg.shape[0]

		res = cv2.matchTemplate(outImg, tempImg, cv2.TM_CCOEFF_NORMED)
		threshold = 0.85	#類似度の閾値
		loc = np.where(res >= threshold)
		for pt in zip(*loc[::-1]):
			matchRes = True
			cv2.rectangle(outImg, pt, (pt[0] + tempWidth, pt[1] + tempHeight), (0,0,255), 2)
			matchPos = (int(pt[0]+(tempWidth/2)), int(pt[1]+(tempHeight/2)))
			matchPos2 = (int(matchPos[0]/IMG_SCALE), int(matchPos[1]/IMG_SCALE))
			break
		return matchRes, matchPos2, outImg
		
	def checkTemplateAll(self, srcImg):
		posDict = {}
		outImg = self.resizeImage(srcImg.copy(), IMG_SCALE)
		for templateName in self.templateImgList.keys():
			matchRes, matchPos, outImg = self.checkTemplate(outImg, templateName)
			if(matchRes):
				posDict[templateName] = matchPos
		return posDict, outImg

	def resizeImage(self, inImg, scale=1.0):
			width = int(inImg.shape[1] * scale)
			height = int(inImg.shape[0] * scale)
			outImg = cv2.resize(inImg, (width, height))
			return outImg


class OperationClass():
	def __init__(self):
		self.adbInstance = AdbClass.getInstance()

	def tap(self, pos, loopCount=1):
		self.adbInstance.tap(pos, loopCount)

	def swipe(self, startPos, endPos, loopCount=1):
		self.adbInstance.swipe(startPos, endPos, loopCount=1)

	def tap_event(self):
		cmd = 'adb shell dd if=/sdcard/renda of=/dev/input/event3'
		self.adbInstance.runCmdNoEcho(cmd, 10)

	def swipe_FlowerUp(self):
		self.adbInstance.swipe((330, 1600), (330, 5600))

	# 勇者メニュー0.2行下に移動
	def swipe_YushaMenu_LittleDown(self):
		self.adbInstance.swipe((330, 2000), (330, 1870))

	# 勇者メニュー１行下に移動
	def swipe_YushaMenu_1LineDown(self):
		self.adbInstance.swipe((330, 2000), (330, 1751))

	# 勇者メニューの最下層まで移動
	def swipe_YushaMenu_AllLineDown(self):
		self.adbInstance.swipe((330, 2675), (330, 0))
		time.sleep(0.400)
		self.adbInstance.swipe((330, 2675), (330, 0))

	# 勇者メニューの一番上まで移動
	def swipe_YushaMenu_AllLineUp(self):
		self.adbInstance.swipe((330, 1880), (330, 6000))

	# 兵士メニュー１行下に移動
	def swipe_SoldierMenu_1Line(self):
		self.adbInstance.swipe((330, 2000), (330, 1781))

	# 兵士メニューの最下層まで移動
	def swipe_SoldierMenu_AllLineDown(self):
		self.adbInstance.swipe((330, 2675), (330, 0))


# 勇者自動生成処理
class AutoYushaCreateClass():
	def __init__(self):
		self.opeInstance = OperationClass()
		self.thLoopFlag = True
		self.th_autoYushaCreateFlag = False
		self.th = threading.Thread(target=self.th_autoYushaCreate)
		self.th.start()

	def th_autoYushaCreate(self):
		count = 0
		while(self.thLoopFlag):
			print('                create ' + str(count))
			if(self.th_autoYushaCreateFlag):
				self.opeInstance.tap((720, 1780), 5)
				self.opeInstance.tap_event()
				#time.sleep(0.100)

				count = count + 1
				if(count>=1):
					count = 0
					self.opeInstance.swipe_FlowerUp()
			else:
				time.sleep(0.5)

	def start(self):
		self.th_autoYushaCreateFlag = True

	def stop(self):
		self.th_autoYushaCreateFlag = False
	
	def destroy(self):
		self.thLoopFlag = False


# 勇者自動育成処理
class AutoYushaUpdateClass():
	UPDATE_NONE = 0
	UPDATE_YUSHA = 1
	UPDATE_SOLDIER = 2

	def __init__(self):
		self.opeInstance = OperationClass()
		self.thLoopFlag = True
		self.th_autoYushaUpdateStatus = AutoYushaUpdateClass.UPDATE_NONE
		self.th = threading.Thread(target=self.th_autoYushaUpdate)
		self.th.start()

	def th_autoYushaUpdate(self):
		while(self.thLoopFlag):
			print('        update')
			if(AutoYushaUpdateClass.UPDATE_YUSHA == self.th_autoYushaUpdateStatus):
				self.opeInstance.tap((1370, 1880))	# ☓マーク
				self.opeInstance.tap((200, 2840))	# 勇者メニュー
				self.opeInstance.swipe_YushaMenu_AllLineUp()
				for count in range(22):
					# if(AutoYushaUpdateClass.UPDATE_YUSHA != self.th_autoYushaUpdateStatus):
					# 	break
					if(not self.thLoopFlag):
						break
					self.opeInstance.tap((1300, 2200), 3)	# 獲得＆レベルアップ
					self.opeInstance.swipe_YushaMenu_LittleDown()
					#time.sleep(0.050)
					print('        update count=' + str(count))
				#time.sleep(0.050)
			elif(AutoYushaUpdateClass.UPDATE_SOLDIER == self.th_autoYushaUpdateStatus):
				self.opeInstance.tap((1370, 1880))	# ☓マーク
				self.opeInstance.tap((600, 2840))	# 兵士メニュー
				# TODO: 3回固定ではなく、画面キャプチャから判定
				for count in range(5):
					if(not self.thLoopFlag):
						break
					self.opeInstance.swipe_SoldierMenu_AllLineDown()
					self.opeInstance.tap((1180, 2270))	# 獲得＆レベルアップ
				self.th_autoYushaUpdateStatus = AutoYushaUpdateClass.UPDATE_YUSHA
				print('Update Yusha Mode')
			else:
				time.sleep(0.500)

	def startYusha(self):
		self.th_autoYushaUpdateStatus = AutoYushaUpdateClass.UPDATE_YUSHA
	
	def startSoldier(self):
		self.th_autoYushaUpdateStatus = AutoYushaUpdateClass.UPDATE_SOLDIER

	def stop(self):
		self.th_autoYushaUpdateStatus = AutoYushaUpdateClass.UPDATE_NONE
	
	def destroy(self):
		self.thLoopFlag = False


if __name__ == '__main__':
	# 新ダンジョン移行不可
	EndlessFlag = False

	# 連続タップスレッド起動
	th_Create = AutoYushaCreateClass()

	# 勇者成長スレッド起動
	th_Update = AutoYushaUpdateClass()

	# マッチング用初期化
	sp = ScreenProcClass()

	# 操作用初期化
	adbInstance = AdbClass.getInstance()
	opeInstance = OperationClass()

	# 状態初期化
	Status = STATUS_STARTING
	StartTime = time.time()
	EntTime = 5*60

	while(True):
		print('main ' + str(time.time()-StartTime))
		if(STATUS_STARTING == Status):
			StartTime = time.time()
			# 各スレッドの動作を開始
			#th_Create = AutoYushaCreateClass()
			th_Create.start()
			#th_Update = AutoYushaUpdateClass()
			th_Update.startYusha()
			# 5sec待って画面から次状態を判定
			time.sleep(5)
			img = adbInstance.screenCapCv2()
			posList, img2 = sp.checkTemplateAll(img)
			if('quest_start' in posList.keys()):
				print('Status: QUEST')
				EntTime = 13*60
				opeInstance.tap((720, 1780))
				Status = STATUS_QUEST
			else:
				print('Status: NORMAL')
				EntTime = 5*60
				Status = STATUS_NORMAL
		
		elif((STATUS_NORMAL == Status) or (STATUS_QUEST == Status)):
			if(EndlessFlag):
				# 全スキル使用
				img = adbInstance.screenCapCv2()
				posList, img2 = sp.checkTemplateAll(img)
				if('skill_1' in posList.keys()):
					opeInstance.tap(posList['skill_1'])
					time.sleep(0.050)
				if('skill_2' in posList.keys()):
					opeInstance.tap(posList['skill_2'])
					time.sleep(0.050)
				if('skill_3' in posList.keys()):
					opeInstance.tap(posList['skill_3'])
					time.sleep(0.050)
				if('skill_4' in posList.keys()):
					opeInstance.tap(posList['skill_4'])
					time.sleep(0.050)
				
			# 開始から一定時間経過で終了処理へ移行
			elif((time.time() - StartTime) > EntTime):
			# else:
				# 各スレッドの動作を停止
				th_Create.stop()
				th_Update.stop()
				#th_Create.destroy()
				#th_Update.destroy()
				#time.sleep(1.000)

				opeInstance.tap((1370, 1880))	# ☓マーク
				opeInstance.tap((200, 2840))	# 勇者メニュー
				opeInstance.swipe_YushaMenu_AllLineDown()

				# 暫定対処
				opeInstance.tap((1200, 2250))	# スキル 究極召喚 獲得

				# 移動前に全スキル使用 (最終画面のスクリーンショット保存)
				savePath = r'C:\temp_py\svn\svn_yusha\trunk\clear\clear_' + str(datetime.datetime.now()) + '.png'
				img = adbInstance.screenCapCv2(True, savePath)

				# img = adbInstance.screenCapCv2()
				posList, img2 = sp.checkTemplateAll(img)
				if('red_treasure' in posList.keys()):
					for i in range(10):
						opeInstance.tap(posList['red_treasure'])
						time.sleep(0.2)
				
				if('skill_1' in posList.keys()):
					opeInstance.tap(posList['skill_1'])
					# time.sleep(0.050)
				# if('skill_2' in posList.keys()):
				# 	opeInstance.tap(posList['skill_2'])
				# 	# time.sleep(0.050)
				# if('skill_3' in posList.keys()):
				# 	opeInstance.tap(posList['skill_3'])
				# 	# time.sleep(0.050)
				# if('skill_4' in posList.keys()):
				# 	opeInstance.tap(posList['skill_4'])
				# 	# time.sleep(0.050)
				
				# 新ダンジョンへ移動
				print('Go to NextDangeon')
				opeInstance.tap((1300, 2630))	# 新ダンジョン
				opeInstance.tap((920, 1850))	# 新しいダンジョンに移動する「はい」
				opeInstance.tap((520, 1900))	# 時間制限ランキングに参加するか「参加しない」
				Status = STATUS_STARTING
				print('Statis: STARTING')
		else:
			pass

		#画像判定で兵士updateするかを判定
		if(STATUS_QUEST == Status):
			# クエスト中のみ兵士アップデートを実施
			img = adbInstance.screenCapCv2()
			matchRes, _matchPos, img2 = sp.checkTemplate(img, 'exclamation_large')
			if(matchRes):
				print('Update Soldier Mode')
				th_Update.startSoldier()
		
		time.sleep(5)

# メモ
#tap((700, 1800))	# 青宝箱 開始(動画を見る)
#tap((1340, 100))	# 青宝箱 CM終了後(☓)
#tap((700, 1750))	# 青宝箱 終了(閉じる)
