"""
class Time:

Generate time data (Day, Hour, Minutes, Seconds) based on video frame and starting hour
Cheat permits to allow fake hours generation for testing purposes (it accelerates the time)

Usage:

t = Time(fps_in_video, max_number_of_frames, cheat=True)
t.up(frame_id)

"""

class Time(object):
	def __init__(self,fps,framenum,basetime = [0,14,31,0],cheat=False):
		super().__init__()
		self.fps = int(fps)
		self.framenum = int(framenum)
		self.d,self.h,self.m,self.s = basetime
		self.cheat=cheat

	def check(self):
		if self.s==60:
			self.s=0
			self.m+=1
		if self.m == 60:
			self.m=0
			self.h+=1
		if self.h == 24:
			self.h = 0
			self.d+=1

	def up(self,framenumber):
		if self.cheat:
			self.s+=1
			if (framenumber%2)==0 and (framenumber != 0):
				self.m+=1
			self.check()
		else:
			if (framenumber%self.fps)==0 and (framenumber != 0):
				self.s+=1
				self.check()
		return '{}:{}:{}:{}'.format(self.d,self.h,self.m,self.s)

if __name__ == "__main__":
	fps = 25
	duree = 1500
	t = Time(fps,duree,cheat=True)
	for i in range(duree):
		print(t.up(i))