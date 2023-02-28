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
