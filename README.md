# Feedback Management System

This is our mini project for Advance Full Stack. It is a small app where a user can register, log in and submit feedback about a service, event or experience. After login the user can see only the feedback they have submitted.

The backend is made with FastAPI and SQLite and the frontend is made with React. We used Docker for the backend and deployed it on AWS EC2 using GitHub Actions.

Team: Jyoshna, Monica, Madiha

## Folders

```
feedback-management
  backend
    main.py           - all the API endpoints
    functions.py      - database tables and database functions, tokens, password hashing
    requirements.txt
    dockerfile
  frontend
    src
      App.jsx         - API_URL, tokens and all fetch calls
      components
        Register.jsx
        Login.jsx
        Dashboard.jsx
        FeedbackList.jsx
  .github/workflows/deploy.yml
```

## Database

We used one SQLite file called `feedback.db` with two tables.

- users - id, username, email, hashed_password, created_at
- feedback - id, user_id, subject, message, rating, created_at

Passwords are hashed using argon2 before saving. Every feedback row has the user_id of the person who submitted it, so one user cannot see another user's feedback.

## API

Backend runs on port 8001.

| # | What it does | Method | Path | Request body | Success code |
|---|---|---|---|---|---|
| A1 | Register a new user | POST | /register | username, email, password | 201 |
| A2 | Login and get access token and refresh token | POST | /login | email, password | 200 |
| A3 | Get a new access token using refresh token | POST | /refresh | refresh token in `refresh-token` header | 200 |
| E1 | Get all feedback of the logged in user | GET | /feedback | access token in `token` header | 200 |
| E2 | Submit new feedback | POST | /feedback | subject, message, rating + `token` header | 201 |

Errors we handled:

- Email already registered - 409
- Wrong email or password - 401
- Invalid or expired access token / refresh token - 401
- Calling /feedback without token - 401
- Empty fields - 422
- Wrong email format - 422
- Rating less than 1 or more than 5 - 422

Access token is valid for 15 minutes and refresh token for 7 days. When the access token expires, the frontend calls /refresh, gets a new access token and tries again. If the refresh token is also expired the user is logged out.

## How to run on your laptop

Backend:

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

Frontend:

```
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The backend address is written only in one place, `API_URL` in `App.jsx`.

## Docker

```
docker build -t feedback-api ./backend
docker run -d -p 8001:8001 -v ${PWD}/data:/app/data feedback-api
```

## Deployment

When anyone pushes to the main branch, GitHub Actions builds the Docker image, pushes it to Docker Hub, connects to our EC2 instance, removes the old container and starts the new one.

To make sure the data is not lost when the container is replaced, we store feedback.db in the folder `/opt/feedback/data` on EC2 and mount it into the container using

```
-v /opt/feedback/data:/app/data
```

So even after a new deployment, the old users and feedback are still there.

Docker Hub and EC2 details are saved in GitHub Secrets (DOCKERHUB_USERNAME, DOCKERHUB_TOKEN, EC2_HOST, EC2_USER, EC2_SSH_KEY), not in the code.

## Who did what

| Name | Work |
|---|---|
| Jyoshna | Project setup, database tables, password hashing, create token, A1 register, A2 login, dockerfile, Login page |
| Monica | Token checking, A3 refresh, E1 get feedback, refresh token handling in frontend, Dashboard and feedback list, CI/CD and EC2 deployment |
| Madiha | E2 submit feedback with validation, Register page, README |
