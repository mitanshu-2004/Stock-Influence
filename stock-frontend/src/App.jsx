"use client"

import { useCallback, useEffect, useRef, useState } from "react"
import LoadingOverlay from "./components/LoadingOverlay.jsx"
import VariablesSelector from "./components/VariablesSelector.jsx"
import CorrelationMatrix from "./components/CorrelationMatrix.jsx"
import TimeSeriesChart from "./components/TimeSeriesChart.jsx"

const API_URL = import.meta.env.VITE_API_URL;




export default function App() {
  // Inputs
  const [file, setFile] = useState(null)
  const [stockSymbol, setStockSymbol] = useState("AAPL")
  const [startDate, setStartDate] = useState("")
  const [endDate, setEndDate] = useState("")

  // Flow state
  const [loadingGlobal, setLoadingGlobal] = useState(false)
  const [running, setRunning] = useState(false)
  const [sessionId, setSessionId] = useState(null)

  // Variables selection
  const [allVars, setAllVars] = useState([])
  const [selectedVars, setSelectedVars] = useState([])

  // Visualizations
  const [matrixData, setMatrixData] = useState(null)
  const [tsData, setTsData] = useState(null)

  // UI state
  const [errorMsg, setErrorMsg] = useState(null)

  // Debounce
  const debounceRef = useRef(null)

  const hasSelection = selectedVars.length >= 2
  const showVisualize = allVars.length > 0
  const showResults = hasSelection && matrixData && tsData

  const onToggleVar = useCallback((col) => {
    setSelectedVars((prev) => (prev.includes(col) ? prev.filter((c) => c !== col) : [...prev, col]))
  }, [])

  const handleSelectAll = useCallback(() => {
    setSelectedVars(allVars)
  }, [allVars])

  const handleClearSelection = useCallback(() => {
    setSelectedVars([])
  }, [])

  const runAnalysis = useCallback(async () => {
    try {
      setErrorMsg(null)
      if (!file) throw new Error("Please select a CSV file.")

      setRunning(true)
      setLoadingGlobal(true)
      setMatrixData(null)
      setTsData(null)
      setAllVars([])
      setSelectedVars([])

      // 1) Upload file
      const formData = new FormData()
      formData.append("file", file)
      const uploadOptions = { method: "POST", body: formData }
      const uploadRes = await fetch(`${API_URL}/upload`, uploadOptions)
      const uploadJson = await uploadRes.json()
      if (!uploadRes.ok) throw new Error(`Upload failed: ${uploadJson?.detail || uploadRes.statusText}`)

      const newSessionId = uploadJson.session_id
      setSessionId(newSessionId)

      // Set dates if server validated a range
      const dateRange = uploadJson?.validation_result?.data_quality?.date_range
      if (dateRange) {
        setStartDate((s) => s || dateRange.start || "")
        setEndDate((e) => e || dateRange.end || "")
      }

      // 2) Stock analysis
      const stockPayload = {
        stock_symbol: stockSymbol,
        start_date: startDate || dateRange?.start || "",
        end_date: endDate || dateRange?.end || "",
      }
      const stockOptions = {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(stockPayload),
      }
      const stockRes = await fetch(`${API_URL}/stock-analysis/${newSessionId}`, stockOptions)
      const stockJson = await stockRes.json()
      if (!stockRes.ok) throw new Error(`Stock analysis failed: ${stockJson?.detail || stockRes.statusText}`)

      // 3) Info -> columns
      const infoRes = await fetch(`${API_URL}/data/${newSessionId}/info`)
      const infoJson = await infoRes.json()
      const merged = infoJson?.merged_numeric_columns
      if (!merged || !Array.isArray(merged) || merged.length === 0) {
        throw new Error("Could not retrieve column information")
      }
      setAllVars(merged)
      setSelectedVars(merged) // default select all
    } catch (err) {
      setErrorMsg(err.message || "Something went wrong")
    } finally {
      setRunning(false)
      setLoadingGlobal(false)
    }
  }, [file, stockSymbol, startDate, endDate])

  const updateVisualizations = useCallback(async () => {
    if (!sessionId) return
    if (selectedVars.length < 2) {
      setMatrixData(null)
      setTsData(null)
      return
    }
    try {
      setErrorMsg(null)
      // matrix
      const matrixPayload = { chart_type: "correlation_matrix", variables: selectedVars }
      const matrixOptions = {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(matrixPayload),
      }
      const mRes = await fetch(`${API_URL}/visualization/${sessionId}?source=merged`, matrixOptions)
      const mJson = await mRes.json()
      if (!mRes.ok) throw new Error(`Matrix visualization failed: ${mJson?.detail || mRes.statusText}`)
      setMatrixData(mJson)

      // time series
      const tsPayload = { chart_type: "time_series", variables: selectedVars }
      const tsOptions = {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(tsPayload),
      }
      const tRes = await fetch(`${API_URL}/visualization/${sessionId}?source=merged`, tsOptions)
      const tJson = await tRes.json()
      if (!tRes.ok) throw new Error(`Time series visualization failed: ${tJson?.detail || tRes.statusText}`)
      setTsData(tJson)
    } catch (err) {
      setErrorMsg(err.message || "Failed to render visualizations")
    }
  }, [sessionId, selectedVars])

  // Debounce variable changes
  useEffect(() => {
    if (!sessionId) return
    if (debounceRef.current) clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => {
      updateVisualizations()
    }, 300)
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current)
    }
  }, [selectedVars, sessionId, updateVisualizations])

  const runBtnText = running ? "Processing..." : "Run Analysis"

  return (
    <>
      <LoadingOverlay show={loadingGlobal} />

      <main className="container mt-4 mb-5">
        {/* Inline error banner (replaces window.alert) */}
        {errorMsg && (
          <div className="alert alert-danger alert-dismissible fade show" role="alert">
            <strong>Error:</strong> {errorMsg}
            <button type="button" className="btn-close" aria-label="Close" onClick={() => setErrorMsg(null)} />
          </div>
        )}

        <header className="hero-section">
          <h1 className="text-balance">Coincidence Finder</h1>
          <p className="lead text-pretty">
            Discover unexpected correlations between your data and stock market movements.
          </p>
        </header>

        {/* Step 1: Analysis Setup */}
        <section className="content-card">
          <div className="step-header">
            <div className="step-number" aria-hidden="true">
              1
            </div>
            <h2 className="step-title h5 m-0">Analysis Setup</h2>
          </div>

          <div className="row g-3">
            <div className="col-md-12">
              <label htmlFor="csv-file" className="form-label">
                Upload Your CSV Data File
              </label>
              <input
                id="csv-file"
                className="form-control"
                type="file"
                accept=".csv"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
              />
              {/* Show selected filename */}
              {file && (
                <div className="form-text mt-1" id="file-help">
                  Selected file: <strong>{file.name}</strong>
                </div>
              )}
            </div>

            <div className="col-md-4">
              <label htmlFor="stock-symbol" className="form-label">
                Stock Symbol
              </label>
              <input
                id="stock-symbol"
                className="form-control"
                type="text"
                value={stockSymbol}
                onChange={(e) => setStockSymbol(e.target.value)}
                placeholder="e.g., AAPL, GOOGL"
              />
            </div>

            <div className="col-md-4">
              <label htmlFor="start-date" className="form-label">
                Start Date
              </label>
              <input
                id="start-date"
                className="form-control"
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </div>

            <div className="col-md-4">
              <label htmlFor="end-date" className="form-label">
                End Date
              </label>
              <input
                id="end-date"
                className="form-control"
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>
          </div>
        </section>

        {/* Run button */}
        <div className="text-center mb-5">
          <button
            type="button"
            className="btn btn-primary btn-lg"
            onClick={runAnalysis}
            disabled={running || !file}
            aria-busy={running}
            aria-describedby={file ? undefined : "file-help"}
            title={!file ? "Please select a CSV file to enable analysis" : undefined}
          >
            {running && <span className="spinner-border spinner-border-sm" role="status" aria-hidden="true" />}
            <span className="btn-text ms-1">{runBtnText}</span>
          </button>
        </div>

        {/* Step 2: Visualize */}
        {showVisualize && (
          <section className="content-card fade-in">
            <div className="step-header">
              <div className="step-number" aria-hidden="true">
                2
              </div>
              <h2 className="step-title h5 m-0">Select Variables to Visualize</h2>
            </div>
            <p className="text-muted mb-3">
              Choose the variables from your data you want to compare with the stock price.{" "}
              <span className="fw-semibold">{selectedVars.length}</span> of{" "}
              <span className="fw-semibold">{allVars.length}</span> selected.
            </p>

            <VariablesSelector
              variables={allVars}
              selected={selectedVars}
              onToggle={onToggleVar}
              onSelectAll={handleSelectAll}
              onClear={handleClearSelection}
            />
          </section>
        )}

        {/* Results */}
        {hasSelection && (
          <section id="results-section" className="fade-in">
            <div className="content-card">
              <h3 className="h5">Correlation Matrix</h3>
              <p className="text-muted mb-3" id="corr-desc">
                Hover over cells to see correlation strength. Blue indicates a positive correlation, red indicates a
                negative one.
              </p>
              {matrixData ? (
                <CorrelationMatrix vizData={matrixData} />
              ) : (
                <p className="text-muted">Select at least two variables to render the matrix.</p>
              )}
            </div>

            <div className="content-card">
              <h3 className="h5">Time Series Comparison</h3>
              <p className="text-muted mb-3">
                A visual comparison of your selected variables and the stock's closing price over time.
              </p>
              {tsData ? (
                <TimeSeriesChart vizData={tsData} />
              ) : (
                <p className="text-muted">Select at least two variables to render the chart.</p>
              )}
            </div>
          </section>
        )}
      </main>
    </>
  )
}
