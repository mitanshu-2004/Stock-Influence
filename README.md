# Stock Analysis Platform

This project is a web-based application that allows users to analyze the correlation between their own time-series data and the historical performance of a stock. Users can upload a CSV file, and the application will merge it with stock data from Yahoo Finance, calculate correlations, and visualize the results.

## Features

*   **CSV Upload**: Upload your own time-series data in CSV format.
*   **Stock Data Integration**: Fetches historical stock data from Yahoo Finance.
*   **Correlation Analysis**: Calculates Pearson, Spearman, and Kendall correlations between your data and the stock's performance.
*   **Interactive Visualizations**:
    *   **Correlation Matrix**: A color-coded matrix to quickly identify strong correlations.
    *   **Time-Series Chart**: A chart to visually compare your data with the stock's price over time.
*   **Session Management**: Each upload creates a new session, allowing you to work with multiple datasets.

## Tech Stack

### Backend

*   **Framework**: FastAPI
*   **Data Validation**: Pydantic
*   **Data Analysis**: Pandas, NumPy, SciPy
*   **Stock Data**: `yfinance`

### Frontend

*   **Framework**: React

## Getting Started

### Prerequisites

*   Python 3.7+
*   Node.js 14+
*   npm

### Installation and Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd stock-analysis-platform
    ```

2.  **Backend Setup:**
    ```bash
    cd stock-backend
    pip install -r requirements.txt
    ```

3.  **Frontend Setup:**
    ```bash
    cd ../stock-frontend
    npm install
    ```

### Running the Application

1.  **Start the Backend Server:**
    From the `stock-backend` directory, run:
    ```bash
    uvicorn app:app --reload
    ```
    The backend will be running at `http://127.0.0.1:8000`.

2.  **Start the Frontend Development Server:**
    From the `stock-frontend` directory, run:
    ```bash
    npm run dev
    ```
    The frontend will be running at `http://localhost:5173`.

3.  **Open the application in your browser** at `http://localhost:5173`.

## How to Use

1.  **Upload a CSV file**: The CSV file must contain at least one date column and one numeric data column.
2.  **Enter a stock symbol**: For example, `AAPL` for Apple Inc.
3.  **Select a date range**: The application will try to auto-fill the date range based on your CSV data.
4.  **Click "Run Analysis"**: The backend will process your data and the stock data.
5.  **Explore the visualizations**:
    *   Use the variable selector to choose which of your data columns to compare with the stock data.
    *   Hover over the correlation matrix to see detailed correlation coefficients.
    *   Analyze the time-series chart to see how your data trends with the stock's closing price.
