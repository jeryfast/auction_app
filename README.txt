Installation

1. Clone the Repository
git clone https://github.com/your-username/auction-engine.git
Create a .env file in the project root with the following content:
docker-compose up --build
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser

Testing
docker-compose exec web pytest

define this variables in .env file
TEST_USER_NAME=
TEST_USER_PASSWORD=
TEST_USER_NAME1=
TEST_USER_PASSWORD1=
SENDGRID_API_KEY=
SENDGRID_FROM=
TEST_USER_EMAIL=
TEST_USER_EMAIL1=