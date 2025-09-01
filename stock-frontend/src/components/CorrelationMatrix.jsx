function cellBg(c) {
  const alpha = Math.min(1, Math.max(0, Math.abs(c) * 0.8 + 0.2))
  return c > 0
    ? `rgba(13, 110, 253, ${alpha})` // blue-ish for positive
    : `rgba(220, 53, 69, ${alpha})` // red-ish for negative
}

export default function CorrelationMatrix({ vizData }) {
  if (!vizData?.data?.columns || !vizData?.data?.values) return null

  const { columns, values } = vizData.data

  return (
    <div id="correlation-matrix-container" className="table-responsive">
      <table className="table table-bordered text-center table-sm" aria-describedby="corr-caption">
        <caption id="corr-caption" className="visually-hidden">
          Correlation matrix showing pairwise correlations. Positive values are blue; negative values are red.
        </caption>
        <thead>
          <tr>
            <th aria-hidden="true" />
            {columns.map((c) => (
              <th className="align-middle" key={`col-${c}`} scope="col">
                {c}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {values.map((row, i) => (
            <tr key={`row-${columns[i]}`}>
              <th className="align-middle" scope="row">
                {columns[i]}
              </th>
              {row.map((v, j) => (
                <td
                  key={`cell-${i}-${j}`}
                  className="correlation-cell align-middle"
                  style={{
                    cursor: "pointer",
                    backgroundColor: cellBg(v),
                    color: Math.abs(v) > 0.5 ? "white" : undefined,
                  }}
                  title={`Correlation: ${v.toFixed(3)}`}
                >
                  {v.toFixed(2)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
