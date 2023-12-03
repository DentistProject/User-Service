# Users Service

This service handles all user related functions, CRUD operations, and authentication.

# Setup

## Local install
Clone the latest code
```
git clone git@git.chalmers.se:courses/dit355/2023/student-teams/dit356-2023-04/users-service.git
```
If you do not have pipenv:
``` pip install pipenv ```<br/>

Otherwise start the virtualenv:
```
pipenv shell
```
Now install required dependencies from requirements.txt:
```
pip install -r requirements.txt
```
Check that all depencies have been correctly installed by running ```pip freeze```

### Setup database
Install postgreSQL if you have not, then create an empty database.

In the repository, create a ```.env``` file in the root directory, same directory as ```.env.dist```, and follow the instructions inside ```.env.dist```.

Now you have to apply django database migrations, first run:
```
python manage.py makemigrations
```
Then:
```
python manage.py migrate
```
Whenever you modify the database model, please redo this step or the changes will not be applied.

### Running the server
To start the service, be in the root directory, you can also specify the port (Optional):
```
python manage.py runserver

python manage.py runserver 127.0.0.1:8001
```

## Docker

Must have docker installed on your computer.

Run docker-compose.yml
```
docker-compose up
```
Now apply the same database migration process:
```
docker-compose run web python manage.py migrate
```
where ```web``` is the service name specified in docker-compose.yml.

Note that the data in this container is persistent storage, and will only be lost if you delete the container.
___
</br>
If you just want to run it as a docker container while still using your existing database, it is a lot simpler.

In root directory, run:

```
docker build -t name .

docker run -p computer_port:container_port your_image_name
```

When you do this, you must also set the database host to ```host.internal.docker``` in ```settings.py``` in order for the container to access the postgres database running on your machine, as the container's localhost is different from your localhost.


