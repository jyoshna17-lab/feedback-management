# Feedback Management System

This is our mini project for Advance Full Stack. It is a small app where a user can register, log in and submit feedback about a service, event or experience. After login the user can see only the feedback they have submitted, not anyone else's.

The backend is made with FastAPI and SQLite and the frontend is made with React. We put the backend in a Docker container and deployed it on AWS EC2. Every time we push to GitHub, GitHub Actions deploys the new version automatically.

Team: Jyoshna, Monica, Madiha

## Technologies used

- Backend - Python, FastAPI, SQLAlchemy, SQLite
- Login and security - JWT (PyJWT) for access and refresh tokens, argon2 for password hashing
- Frontend - React with Vite, react-router for pages
- Deployment - Docker, Docker Hub, AWS EC2 (Amazon Linux), GitHub Actions

## Folders

```
feedback-management
  backend
    main.py           - all the API endpoints and input checks
    functions.py      - database tables, database functions, tokens, password hashing
    requirements.txt  - python packages
    dockerfile        - to build the backend docker image
  frontend
    src
      App.jsx         - API_URL, tokens, all fetch calls and page routes
      components
        Register.jsx      - register page
        Login.jsx         - login page
        Dashboard.jsx     - page after login, shows the user's feedback
        FeedbackList.jsx  - list of feedback shown on the dashboard
  .github/workflows/deploy.yml  - CI/CD to build, push and deploy
```

## Database

We used one SQLite file called `feedback.db` with two tables.

**users**

| Column | Meaning |
|---|---|
| id | user id |
| username | name of the user |
| email | email, used for login, cannot be repeated |
| hashed_password | password after hashing with argon2 (we never save the real password) |
| created_at | date and time of registration |

**feedback**

| Column | Meaning |
|---|---|
| id | feedback id |
| user_id | id of the user who submitted it |
| subject | title of the feedback |
| message | the feedback text |
| rating | 1 to 5 |
| created_at | date and time of submission |

Every feedback row has the user_id of the person who submitted it. When a user asks for their feedback we only return rows with their user_id, so one user cannot see another user's feedback.

## API

Backend runs on port 8001. You can test all the APIs at http://127.0.0.1:8001/docs

| # | What it does | Method | Path | Request body | Success code |
|---|---|---|---|---|---|
| A1 | Register a new user | POST | /register | username, email, password | 201 |
| A2 | Login and get access token and refresh token | POST | /login | email, password | 200 |
| A3 | Get a new access token using refresh token | POST | /refresh | refresh token in `refresh-token` header | 200 |
| E1 | Get all feedback of the logged in user | GET | /feedback | access token in `token` header | 200 |
| E2 | Submit new feedback | POST | /feedback | subject, message, rating + `token` header | 201 |

Errors we handled:

| Case | Status | Message |
|---|---|---|
| Registering with an email that already exists | 409 | Email already registered |
| Login with wrong email or password | 401 | Invalid email or password |
| Invalid or expired access token | 401 | Invalid or expired access token |
| Invalid or expired refresh token | 401 | Invalid or expired refresh token |
| Calling /feedback without a token | 401 | Invalid or expired access token |
| Empty username, password, subject or message | 422 | ... cannot be empty |
| Wrong email format | 422 | Invalid email format |
| Rating less than 1 or more than 5 | 422 | Rating must be between 1 and 5 |

### How the tokens work

- When the user logs in, the backend gives two tokens - an access token (valid for 15 minutes) and a refresh token (valid for 7 days).
- Each token has a `token_type` inside it ("access" or "refresh"), so an access token cannot be used in place of a refresh token.
- The frontend sends the access token in the `token` header for /feedback.
- When the access token expires, the backend returns 401. The frontend then calls /refresh with the refresh token, gets a new access token and sends the request again.
- If the refresh token is also expired, the user is logged out and taken to the login page.

## How to run on your laptop

### Backend

The database is stored in `/app/data/feedback.db` (same path as inside Docker), so first make this folder once:

```
mkdir C:\app\data
```

Then:

```
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

Open http://127.0.0.1:8001/docs to test the APIs.

### Frontend

```
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The backend address is written only in one place, `API_URL` in `App.jsx`.

### Using the app

1. Open the Register page, enter username, email and password and click Register.
2. You will be taken to the Login page. Login with the same email and password.
3. You will be taken to the Dashboard. It loads your feedback automatically. If you have not submitted any feedback it shows "You have not submitted any feedback yet."
4. Click Logout to go back to the Login page.

New feedback can be submitted from http://127.0.0.1:8001/docs using POST /feedback.

## Docker

```
docker build -t feedback-api ./backend
docker run -d -p 8001:8001 -v ${PWD}/data:/app/data feedback-api
```

## Deployment

We have one EC2 instance (Amazon Linux) with Docker installed. Port 8001 is open in the security group.

When anyone pushes to the main branch, GitHub Actions does these steps:

1. Builds the Docker image from the backend folder
2. Pushes the image to Docker Hub
3. Connects to our EC2 instance using SSH
4. Pulls the latest image
5. Removes the old container
6. Starts the new container

### Keeping the data safe

If the database is only inside the container, it gets deleted when the old container is removed during deployment. To stop this, we store feedback.db in the folder `/opt/feedback/data` on EC2 and connect it to `/app/data` inside the container using

```
-v /opt/feedback/data:/app/data
```

So even after a new deployment, the old users and feedback are still there. We tested this by adding feedback, pushing a new change and checking that the feedback was still there after the deployment.

Docker Hub and EC2 details are saved in GitHub Secrets (DOCKERHUB_USERNAME, DOCKERHUB_TOKEN, EC2_HOST, EC2_USER, EC2_SSH_KEY), not in the code.

## Our contributions

We all worked on the same GitHub repository and each of us pushed our own part.

### Jyoshna

Backend

- Created the GitHub repository and added Monica and Madiha as collaborators
- Made the first project structure (backend, frontend and workflow folders)
- `functions.py` - database connection, `users` and `feedback` tables
- `functions.py` - `register_user()` which checks for a duplicate email and saves the user with a hashed password (argon2)
- `functions.py` - `verify_login()` which checks the email and password and returns the tokens
- `functions.py` - `create_token()` which makes the access token (15 min) and refresh token (7 days)
- `main.py` - FastAPI app setup and CORS so the React app can call the backend
- `main.py` - `is_valid_email()` to check the email format
- `main.py` - A1 POST /register (201, 409 for same email, 422 for empty fields and wrong email)
- `main.py` - A2 POST /login (200 with tokens, 401 for wrong email or password)
- `requirements.txt` and `dockerfile`

Frontend

- Created the React app with Vite
- `App.jsx` - `API_URL`, the token states and the `login()` function which saves both tokens and goes to the dashboard
- `Login.jsx` - login page with email and password fields and error message

### Monica

Backend

- `functions.py` - `verify_token()` which checks the token signature, expiry and token type
- `functions.py` - `user_exists()` to check the user in the token still exists
- `functions.py` - `get_feedback()` which returns only the logged in user's feedback, newest first
- `main.py` - `check_user()` which reads the token header and returns 401 for missing, invalid or expired tokens
- `main.py` - A3 POST /refresh (200 with new access token, 401 for invalid refresh token or if an access token is sent)
- `main.py` - E1 GET /feedback (200 with the user's feedback, 401 without token)

Frontend

- `App.jsx` - `getNewAccessToken()` which calls /refresh
- `App.jsx` - `loadFeedback()` which calls /feedback and, if the access token has expired, gets a new one and tries again
- `App.jsx` - `logout()` and the /dashboard route
- `Dashboard.jsx` - dashboard page which loads the feedback after login, shows errors and has the logout button
- `FeedbackList.jsx` - shows subject, message, rating and date, and a message when there is no feedback
- Added react-router to the frontend packages

Deployment

- Launched the EC2 instance, installed Docker and opened port 8001
- Created the `/opt/feedback/data` folder on EC2 for the database
- `deploy.yml` - GitHub Actions workflow to build the image, push it to Docker Hub and deploy it on EC2 with the `-v` mount
- Added the Docker Hub and EC2 details to GitHub Secrets

### Madiha

Backend

- `functions.py` - `add_feedback()` which saves the feedback with the logged in user's id
- `main.py` - `FeedbackCreate` model for subject, message and rating
- `main.py` - E2 POST /feedback (201, 422 for empty subject or message and for rating outside 1 to 5, 401 without token)
- The user_id is always taken from the token and never from the request body, so nobody can submit feedback as another user

Frontend

- `App.jsx` - `register()` function and the /register route
- `Register.jsx` - register page with username, email and password fields, error message and success message, then goes to the login page

Documentation

- `README.md`
