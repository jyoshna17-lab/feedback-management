// A2 - Login page
import { useState } from "react";
import { Link } from "react-router";

function Login({ onLogin, error, success }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  function handleSubmit(e) {
    e.preventDefault();               // stop the form from reloading the page
    onLogin(email, password);         // tell App: "log this user in"
  }

  return (
    <div className="card">
      <h1>Login</h1>
      <form onSubmit={handleSubmit}>
        <input type="text" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
        <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
        <button type="submit">Login</button>
      </form>

      {error ? <p className="error">{error}</p> : null}
      {success ? <p className="success">{success}</p> : null}

      <p>New user? <Link to="/register">Register</Link></p>
    </div>
  );
}

export default Login;