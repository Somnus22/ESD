# ESD
1. Ensure your WAMP or MAMP has been started

2. Import the database.sql into your local myPHPAdmin

3. Ensure your Docker engine is up

4. If you're on a Mac, use docker-compose -f mac_compose.yaml up. 

5. If you're on Windows, use docker-compose -f win_compose.yaml up. 

6. If none of these options work, use the standard compose.yaml file but you will need to adjust the  "db_URL" in the environment variable for each of the services - "car_inventory", "rental_log", "report", "users" - to a configuration that suits your mySQL set up.

7. You can import the custom Postman tests to tests if the services are working.

8. You can use JomLetsGo.html to tests the services through our frontend interface.