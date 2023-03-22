# ambassador DRF

### The Ambassador app is built using the Django REST framework and is part of a larger project. It is closely connected to ambassador_vue.

### Setup:

1. Rename `.env.sample` to `.env` and replace the values.
2. Run `docker-compose up` in your terminal.
3. Run `docker ps` to get the ID of the `ambassador_backend` container.
4. Run `docker exec -it <container ID> bash`.
5. In the bash terminal, run the following commands:
- `python manage.py populate_ambassadors`
- `python manage.py populate_orders`
- `python manage.py populate_products` 
to load sample data.

Now everything should now be set up and ready to use.

#### You can find the documentation at http://localhost:8000/api/docs/.

-------------------------------------------------------------
# Django REST framework ambassador app

The app is built with the **Django REST framework** on the backend and **Vue.js** on the frontend. The frontend app: https://github.com/aalug/ambassador_vue  
The app uses:

- Docker
- Postgres
- Redis
- drf-spectacular for documentation

## Getting started

1. Clone the repository.
4. Rename `.env.sample` to `.env` and replace the values
5. Run in your terminal `docker-compose up --build`
6. Now everything should be set up and app's documentation available on http://localhost:8000/api/docs/

## Testing

To run tests:
1. If containers are not running, run in your terminal `docker-compose up`
2. In the second terminal tab, run `docker ps` and get the ID of the app container
3. Run `docker exec -it <container ID> bash` to get access to the container's shell
4. Run `python manage.py test` to run all tests or `python manage.py test <app-name>.tests` to run tests for a specific
   app


## API Endpoints

All endpoints are available on http://localhost:8000/api/docs/.
After running containers, this will provide you with complete and easy-to-use documentation.
It also gives the option to use every endpoint of this API.


### More Information
This app uses djangorestframework-camel-case to enable the server to send and receive data in a format that is compatible with TypeScript. This package provides support for camel-case style serialization and deserialization, which is appropriate for the conventions used in Vue.js.

