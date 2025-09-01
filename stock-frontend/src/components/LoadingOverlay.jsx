export default function LoadingOverlay({ show }) {
  return (
    <div className="loading-overlay" style={{ display: show ? "flex" : "none" }} aria-hidden={!show} aria-live="polite">
      <div className="loading-content">
        <div className="loading-spinner" role="status" aria-label="Loading"></div>
        <h3>Processing Your Data...</h3>
        <p className="text-muted">Finding hidden correlations</p>
      </div>
    </div>
  )
}
