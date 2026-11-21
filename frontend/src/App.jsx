import { useState } from "react";
import { Routes, Route, useNavigate } from "react-router";

import Login from "./components/Login.jsx";
import Dashboard from "./components/Dashboard.jsx";

const API_URL = "http://127.0.0.1:8001";


// ---------- App: keeps the tokens and calls the API ----------
function App() {
  const [accessToken, setAccessToken] = useState("");
  const [refreshToken, setRefreshToken] = useState("");
  const [feedbacks, setFeedbacks] = useState([]);
  const [success, setSuccess] = useState("");   // green message
  const [error, setError] = useState("");       // red message
  const navigate = useNavigate();


// A2 - POST /login
  async function login(email, password) {
    setError("");
    setSuccess("");
    const response = await fetch(API_URL + "/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: email, password: password }),
    });
    const data = await response.json();
    if (response.status !== 200) {
      setError(data.detail);
      return;
    }
    setAccessToken(data.access_token);     // save both tokens
    setRefreshToken(data.refresh_token);
    navigate("/dashboard");                // the dashboard loads the feedback
  }

  // A3 - POST /refresh   (gives a new access token, or "" if the refresh token also expired)
  async function getNewAccessToken() {
    const response = await fetch(API_URL + "/refresh", {
      method: "POST",
      headers: { "refresh-token": refreshToken },
    });
    if (response.status !== 200) {
      return "";
    }
    const data = await response.json();
    setAccessToken(data.access_token);
    return data.access_token;
  }

  // E1 - GET /feedback
  async function loadFeedback() {
    if (accessToken === "") {              // not logged in
      navigate("/login");
      return;
    }
    let response = await fetch(API_URL + "/feedback", {
      headers: { token: accessToken },
    });

    if (response.status === 401) {         // access token expired, so get a new one and try again
      const newToken = await getNewAccessToken();
      if (newToken === "") {
        logout();
        setError("Session expired. Please login again.");
        return;
      }
      response = await fetch(API_URL + "/feedback", {
        headers: { token: newToken },
      });
    }

    const data = await response.json();
    if (response.status !== 200) {
      setError(data.detail);
      return;
    }
    setFeedbacks(data);
  }

  function logout() {
    setAccessToken("");
    setRefreshToken("");
    setFeedbacks([]);
    setSuccess("");
    setError("");
    navigate("/login");
  }

return (
    <>
      <Routes>
        <Route path="/" element={<Login onLogin={login} error={error} success={success} />} />
        <Route path="/login" element={<Login onLogin={login} error={error} success={success} />} />
        <Route
          path="/dashboard"
          element={
            <Dashboard
              feedbacks={feedbacks}
              onLoad={loadFeedback}
              onLogout={logout}
              error={error}
              success={success}
            />
          }
        />
        <Route path="*" element={<h1>404 Not Found</h1>} />
      </Routes>
    </>
  );
}

export default App;