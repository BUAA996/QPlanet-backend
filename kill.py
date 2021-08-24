import os
os.system("ps -ef | grep \"runserver\" > log.txt")
F=open("log.txt","r")
a = F.readline().split()
b = F.readline().split()
print("The process id are %s and %s."%(a[1],b[1]))

os.system("kill -9 " + a[1])
os.system("kill -9 " + b[1])
print("They have been successfully killed!")