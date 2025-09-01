"use client"

import { useMemo, useState } from "react"

export default function VariablesSelector({ variables, selected, onToggle, onSelectAll, onClear }) {
  const [query, setQuery] = useState("")

  const filtered = useMemo(() => {
    if (!query) return variables
    const q = query.toLowerCase()
    return variables.filter((v) => v.toLowerCase().includes(q))
  }, [variables, query])

  return (
    <div>
      <div className="d-flex flex-wrap align-items-center justify-content-between gap-2 mb-3">
        <div className="input-group" style={{ maxWidth: 360 }}>
          <span className="input-group-text" id="search-label">
            Search
          </span>
          <input
            type="search"
            className="form-control"
            placeholder="Filter variables"
            aria-labelledby="search-label"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
        <div className="d-flex gap-2">
          <button
            type="button"
            className="btn btn-outline-secondary btn-sm"
            onClick={() => onClear?.()}
            disabled={selected.length === 0}
          >
            Clear
          </button>
          <button
            type="button"
            className="btn btn-outline-primary btn-sm"
            onClick={() => onSelectAll?.()}
            disabled={selected.length === variables.length}
          >
            Select All
          </button>
        </div>
      </div>

      <div id="variables-container" role="group" aria-label="Select variables">
        {filtered.map((col) => {
          const id = `check-${col}`
          const isChecked = selected.includes(col)
          return (
            <div className="variable-checkbox" key={col}>
              <input type="checkbox" id={id} value={col} checked={isChecked} onChange={() => onToggle(col)} />
              <label htmlFor={id}>{col}</label>
            </div>
          )
        })}
        {filtered.length === 0 && <p className="text-muted m-0">No variables match your search.</p>}
      </div>
    </div>
  )
}
