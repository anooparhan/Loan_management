# Project Setup Instructions

## Overview
This project consists of three Django applications:
1. **loanapp** - Manages loan-related functionalities.
2. **user** - Handles user management.
3. **authentication** - Manages authentication and token generation.

## Requirements
Ensure you have all necessary dependencies installed before running the project. Install them using:

```sh
pip install -r requirements.txt
```

## Superuser Credentials
To access the Django Admin panel and perform administrative actions, use the following superuser credentials:
- **Email:** `admin@gmail.com`
- **Password:** `1234`

## Running the Project
1. Navigate to the project directory and apply migrations:
   ```sh
   python manage.py migrate
   ```

2. Create a superuser (if not already created):
   ```sh
   python manage.py createsuperuser
   ```
   Enter the required details.

3. Start the Django development server:
   ```sh
   python manage.py runserver
   ```
   The application will be available at `http://127.0.0.1:8000/`.

## API Authentication & Usage
Before running API requests, follow these steps:
1. **Create a user:** Register a new user using the user registration API.
2. **Login to generate a token:** Use the authentication API to log in and retrieve an access token.
3. **Use Bearer Token in Postman:** Attach the token as a `Bearer Token` in the Postman Authorization header before making API requests.

## Postman Collection
You can access and test the API endpoints using the provided Postman collection URL:
[Postman Collection](PASTE_YOUR_POSTMAN_URL_HERE)

## Additional Notes
- Make sure the database is properly set up before running the project.
- Check the `settings.py` file to configure database settings if needed.
- If encountering errors, ensure dependencies from `requirements.txt` are installed correctly.

---
This README provides a structured guide to setting up and running the project. Let me know if you need modifications! 🚀

