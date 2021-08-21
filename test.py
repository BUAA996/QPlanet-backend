import qrcode
import platform

img=qrcode.make("http://www.bilibili.com")
with open("test.png","wb") as f:
	img.save(f)