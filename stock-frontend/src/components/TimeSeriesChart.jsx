"use client"

import { useEffect, useRef } from "react"
import { Chart, LineElement, PointElement, LineController, CategoryScale, LinearScale, Tooltip, Legend } from "chart.js"

Chart.register(LineElement, PointElement, LineController, CategoryScale, LinearScale, Tooltip, Legend)

// Limited, accessible palette (max 5 colors): blue, teal, orange, gray, green
const COLORS = ["#0d6efd", "#20c997", "#fd7e14", "#6c757d", "#198754"]

export default function TimeSeriesChart({ vizData }) {
  const canvasRef = useRef(null)
  const chartRef = useRef(null)

  useEffect(() => {
    const ctx = canvasRef.current?.getContext("2d")
    if (!ctx) return

    // destroy prior instance
    if (chartRef.current) {
      chartRef.current.destroy()
      chartRef.current = null
    }

    if (!vizData?.data?.length) return

    const labels = vizData.data[0].x
    const datasets = vizData.data.map((trace, index) => ({
      label: trace.name,
      data: trace.y,
      fill: false,
      borderColor: COLORS[index % COLORS.length],
      backgroundColor: COLORS[index % COLORS.length],
      tension: 0.1,
      pointRadius: 2,
      pointHoverRadius: 5,
      borderWidth: 2,
    }))

    chartRef.current = new Chart(ctx, {
      type: "line",
      data: { labels, datasets },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        interaction: { mode: "index", intersect: false },
        plugins: {
          legend: { position: "top", labels: { boxWidth: 18 } },
          tooltip: {
            backgroundColor: "rgba(0, 0, 0, 0.8)",
            padding: 10,
            cornerRadius: 4,
          },
        },
        scales: {
          y: { beginAtZero: false, ticks: { precision: 2 } },
        },
      },
    })

    return () => {
      if (chartRef.current) {
        chartRef.current.destroy()
        chartRef.current = null
      }
    }
  }, [vizData])

  return <canvas id="time-series-canvas" ref={canvasRef} aria-label="Time series comparison chart" role="img" />
}
