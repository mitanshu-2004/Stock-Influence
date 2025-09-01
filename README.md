# Stock Analysis Platform

This project is a web-based application that allows users to analyze the correlation between their own time-series data and the historical performance of a stock. This application is hosted and can be accessed at [https://stock-influence.vercel.app/](https://stock-influence.vercel.app/). Users can upload a CSV file, and the application will merge it with stock data from Yahoo Finance, calculate correlations, and visualize the results.

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

## How to Use

1.  **Upload a CSV file**: The CSV file must contain at least one date column and one numeric data column.
2.  **Enter a stock symbol**: For example, `AAPL` for Apple Inc.
3.  **Select a date range**: The application will try to auto-fill the date range based on your CSV data.
4.  **Click "Run Analysis"**: The backend will process your data and the stock data.
5.  **Explore the visualizations**:
    *   Use the variable selector to choose which of your data columns to compare with the stock data.
    *   Hover over the correlation matrix to see detailed correlation coefficients.
    *   Analyze the time-series chart to see how your data trends with the stock's closing price.
