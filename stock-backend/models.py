from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date

class StockAnalysisRequest(BaseModel):
    stock_symbol: str
    start_date: date
    end_date: date
    methods: List[str] = Field(default=['pearson', 'spearman'])
    min_correlation: float = Field(default=0.1, ge=0.0, le=1.0)

class VisualizationRequest(BaseModel):
    variables: List[str]
    chart_type: str
    x_var: Optional[str] = None
    y_var: Optional[str] = None

class ErrorResponse(BaseModel):
    detail: str