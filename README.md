# quiz_app
Before running this application make sure that python is installed on your machine.
1.Install xamp for using mysql. create a database named 'quiz' in your php my admin.
2. Clone this repository in a folder.
3. Create a python virtual environment by use this command
```
python -m venv venv
```
4.Activate the virtual environment by using..
```
venv\Scripts\activate
```
5.Now you have to install the all packages related to this project by using..
```
pip install -r requirements.txt
```
6.Then you have to  makemigrations and migrate your database. makemigrations is responsible for creating new migrations based on the changes you have made to your models.
migrate, which is responsible for applying and unapplying migrations. Now use these command
```
py manage.py makemigrations
py manage.py migrate
```
7. Now you have to make a  super user for admin related work. you have use those username and password for admin login.
```
py manage.py createsuperuser
```
8.At last you have to run the server by using this command.
```
py manage.py runserver
```
