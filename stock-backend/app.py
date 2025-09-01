from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from models import  StockAnalysisRequest, VisualizationRequest
from session import SessionManager
from csv_utils import CSVValidator
from analysis import CorrelationAnalyzer
from stock import StockAnalyzer
from visualization import VisualizationEngine
from datetime import datetime
import pandas as pd
import math
from dotenv import load_dotenv
import os

load_dotenv()

def make_json_safe(data):
    if isinstance(data, dict):
        return {k: make_json_safe(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [make_json_safe(i) for i in data]
    elif isinstance(data, float) and not math.isfinite(data):
        return None
    else:
        return data

session_manager = SessionManager()
validator = CSVValidator()
correlation_analyzer = CorrelationAnalyzer()
stock_analyzer = StockAnalyzer()
viz_engine = VisualizationEngine()

app = FastAPI(
    title="CSV & Stock Analysis Platform",
    description="Analyze CSV data and discover correlations with stock market data.",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins = os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "CSV Analysis Platform API",
        "version": "1.1.0"
    }

@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    content = await file.read()
    validation_result = validator.validate_csv(content)
    if not validation_result['is_valid']:
        raise HTTPException(status_code=400, detail=validation_result['error'])
    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    session_manager.create_session(session_id, validation_result)
    return {
        'session_id': session_id,
        'validation_result': {
            'total_rows': validation_result['total_rows'],
            'date_column': validation_result['date_column'],
            'numeric_columns': validation_result['numeric_columns'],
            'data_quality': validation_result['data_quality']
        }
    }


@app.post("/stock-analysis/{session_id}")
async def stock_analysis(session_id: str, request: StockAnalysisRequest):
    session_data = session_manager.get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    custom_data = session_data['data']
    date_column = session_data['date_column']
    
    # Fetch stock data
    stock_data = stock_analyzer.fetch_stock_data(
        request.stock_symbol,
        request.start_date,
        request.end_date
    )
    if stock_data is None:
        raise HTTPException(status_code=400, detail=f"Could not fetch stock data for {request.stock_symbol}")
    
    # Merge datasets
    merged = stock_analyzer.align_and_merge(stock_data, custom_data, date_column)
    if merged.empty:
        raise HTTPException(status_code=400, detail="No overlapping dates found between datasets")
    
    # Prepare variables for correlation analysis
    stock_vars = ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', 'Dividends', 'Stock Splits']
    available_stock_vars = [col for col in stock_vars if col in merged.columns]
    custom_vars = [col for col in merged.columns 
                   if col not in ['date', 'Date'] + stock_vars 
                   and merged[col].dtype in ['float64', 'int64']]
    
    if not available_stock_vars or not custom_vars:
        raise HTTPException(status_code=400, detail="No valid variables found for correlation analysis")
    
    # Use the CorrelationAnalyzer for consistent correlation calculation
    all_vars = available_stock_vars + custom_vars
    correlations = correlation_analyzer.analyze_correlations(
        data=merged,
        numeric_columns=all_vars,
        methods=request.methods,
        min_correlation=request.min_correlation
    )
    
    # Filter to only include stock-to-custom correlations
    stock_custom_correlations = [
        corr for corr in correlations
        if (corr['variable1'] in available_stock_vars and corr['variable2'] in custom_vars) or
           (corr['variable1'] in custom_vars and corr['variable2'] in available_stock_vars)
    ]
    
    # Reformat to match expected output structure
    formatted_correlations = []
    for corr in stock_custom_correlations:
        # Determine which variable is stock and which is custom
        if corr['variable1'] in available_stock_vars:
            stock_var, custom_var = corr['variable1'], corr['variable2']
        else:
            stock_var, custom_var = corr['variable2'], corr['variable1']
        
        formatted_correlations.append({
            'stock_variable': stock_var,
            'custom_variable': custom_var,
            'correlation': corr['correlation'],
            'p_value': corr['p_value'],
            'method': corr['method'],
            'n_observations': corr['n_observations'],
            'significant': corr['significant'],
            'confidence_interval': corr.get('confidence_interval')
        })
    
    # Update session with merged data
    session_manager.update_session(session_id, {
        'merged_data': merged,
        'merged_date_column': 'date',
        'merged_numeric_columns': all_vars
    })
    
    return {'correlations': formatted_correlations}

@app.post("/visualization/{session_id}")
async def create_visualization(
    session_id: str, 
    request: VisualizationRequest,
    source: str = Query("custom", enum=["custom", "merged"])
):
    session_data = session_manager.get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")

    if source == "merged":
        data = session_data.get('merged_data')
        date_column = session_data.get('merged_date_column')
        if data is None or date_column is None:
            raise HTTPException(status_code=400, detail="No merged data found. Run stock analysis first.")
    else:
        data = session_data['data']
        date_column = session_data['date_column']
    
    if request.chart_type == 'correlation_matrix':
        valid_vars = [var for var in request.variables if var in data.columns]
        if len(valid_vars) < 2:
            raise HTTPException(status_code=400, detail="Need at least 2 variables for correlation matrix")
        viz_data = viz_engine.create_correlation_matrix(data[valid_vars])
    elif request.chart_type == 'time_series':
        valid_vars = [var for var in request.variables if var in data.columns]
        if not valid_vars:
            raise HTTPException(status_code=400, detail="No valid variables specified")
        viz_data = viz_engine.create_time_series_data(data, date_column, valid_vars)
    else:
        raise HTTPException(status_code=400, detail="Invalid chart_type")
    
    return make_json_safe(viz_data)

@app.get("/data/{session_id}/info")
async def get_data_info(session_id: str):
    session_data = session_manager.get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
    data = session_data['data']
    info = {
        'session_id': session_id,
        'total_rows': len(data),
        'total_columns': len(data.columns),
        'date_column': session_data['date_column'],
        'numeric_columns': session_data['numeric_columns']
    }
    if 'merged_numeric_columns' in session_data:
        info['merged_numeric_columns'] = session_data['merged_numeric_columns']
    return info


@app.get("/sessions")
async def list_sessions():
    sessions = []
    for session_id, session_data in session_manager.sessions.items():
        sessions.append({
            'session_id': session_id,
            'created_at': session_data['created_at'].isoformat(),
            'last_accessed': session_data['last_accessed'].isoformat(),
            'total_rows': session_data['total_rows'],
            'total_columns': len(session_data['numeric_columns']),
            'date_column': session_data['date_column']
        })
    return {'sessions': sessions}

@app.get("/health")
async def health_check():
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'active_sessions': len(session_manager.sessions)
    }