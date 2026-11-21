// A1 - Register page
import { useState } from "react";
import { Link } from "react-router";

function Register({ onRegister, error, success }) {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  function handleSubmit(e) {
    e.preventDefault();                        // stop the form from reloading the page
    onRegister(username, email, password);     // tell App: "register this user"
  }

  return (
    <div className="card">
      <h1>Register</h1>
      <form onSubmit={handleSubmit}>
        <input type="text" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
        <input type="text" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
        <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
        <button type="submit">Register</button>
      </form>

      {error ? <p className="error">{error}</p> : null}
      {success ? <p className="success">{success}</p> : null}

      <p>Already have an account? <Link to="/login">Login</Link></p>
    </div>
  );
}

export default Register;