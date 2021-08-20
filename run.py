import os

os.system("python manage.py makemigrations")
os.system("python manage.py migrate")
os.system("nohup python manage.py runserver 0.0.0.0:8000 & \n")
print("The backend is running!")