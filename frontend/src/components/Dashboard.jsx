// E1 - Feedback Dashboard
import { useEffect } from "react";
import FeedbackList from "./FeedbackList.jsx";

function Dashboard({ feedbacks, onLoad, onLogout, error, success }) {
  useEffect(() => {
    onLoad();                         // GET /feedback as soon as the dashboard opens
  }, []);

  return (
    <div className="card wide">
      <div className="header">
        <h1>My Feedback</h1>
        <button onClick={onLogout}>Logout</button>
      </div>

      {error ? <p className="error">{error}</p> : null}
      {success ? <p className="success">{success}</p> : null}

      <FeedbackList feedbacks={feedbacks} />
    </div>
  );
}

export default Dashboard;
