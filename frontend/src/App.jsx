import { useState } from "react";
import { Routes, Route, useNavigate } from "react-router";

import Login from "./components/Login.jsx";

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

return (
    <>
      <Routes>
        <Route path="/" element={<Login onLogin={login} error={error} success={success} />} />
        <Route path="/login" element={<Login onLogin={login} error={error} success={success} />} />
        <Route path="*" element={<h1>404 Not Found</h1>} />
      </Routes>
    </>
  );
}

export default App;