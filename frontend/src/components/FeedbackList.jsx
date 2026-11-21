// One feedback from GET /feedback:
// { id, subject, message, rating, created_at }
function FeedbackList({ feedbacks }) {
  return (
    <section>
      {feedbacks.length === 0 ? (
        <p>You have not submitted any feedback yet.</p>
      ) : (
        <ul className="list">
          {feedbacks.map((feedback) => (
            <li key={feedback.id} className="item">
              <h2>{feedback.subject}</h2>
              <p>{feedback.message}</p>
              <p className="stars">Rating: {feedback.rating} / 5</p>
              <p className="muted">Submitted on: {feedback.created_at}</p>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

export default FeedbackList;
