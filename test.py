'''
import qrcode
import platform

img=qrcode.make("http://www.bilibili.com")
with open("test.png","wb") as f:
	img.save(f)
'''

a = [1,2,3]
print(a)
b = str(a)
print(b)
print()