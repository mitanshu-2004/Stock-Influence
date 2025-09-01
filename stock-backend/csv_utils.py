import pandas as pd
import io
from config import MAX_FILE_SIZE

class CSVValidator:
    date_patterns = ['date', 'time', 'timestamp', 'day', 'month', 'year', 'created', 'updated']

    def validate_csv(self, file_content: bytes) -> dict:
        try:
            # Check file size
            if len(file_content) > MAX_FILE_SIZE:
                return {
                    'is_valid': False, 
                    'error': f'File size exceeds maximum limit of {MAX_FILE_SIZE // (1024*1024)}MB'
                }
            
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(io.BytesIO(file_content), encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    continue
            
            if df is None:
                return {'is_valid': False, 'error': 'Could not read CSV file with any supported encoding'}
            
            # Basic validation
            if df.empty:
                return {'is_valid': False, 'error': 'CSV file is empty'}
            
            if len(df.columns) < 2:
                return {'is_valid': False, 'error': 'CSV must have at least 2 columns'}
            
            # Clean column names (remove whitespace)
            df.columns = df.columns.str.strip()
            
            # Detect date column
            date_column = self._detect_date_column(df)
            if not date_column:
                return {'is_valid': False, 'error': 'No valid date column detected. Column names should contain: date, time, timestamp, etc.'}
            
            # Convert and validate date column
            original_length = len(df)
            df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
            df = df.dropna(subset=[date_column])
            
            if df.empty:
                return {'is_valid': False, 'error': 'No valid dates found in date column'}
            
            
            # Identify numeric columns
            numeric_columns = []
            for col in df.columns:
                if col != date_column:
                    # Try to convert to numeric
                    numeric_series = pd.to_numeric(df[col], errors='coerce')
                    if not numeric_series.isna().all():  # At least some valid numeric values
                        df[col] = numeric_series
                        numeric_columns.append(col)
            
            if not numeric_columns:
                return {'is_valid': False, 'error': 'No numeric variables found for analysis'}
            
            # Sort by date
            df = df.sort_values(date_column).reset_index(drop=True)
            
            # Check for minimum data requirements
            if len(df) < 10:
                return {'is_valid': False, 'error': 'Need at least 10 valid data points for analysis'}
            
            
            return {
                'is_valid': True,
                'data': df,
                'date_column': date_column,
                'numeric_columns': numeric_columns,
                'total_rows': len(df),
                'original_rows': original_length,
                'data_quality': {
                    'date_coverage': len(df) / original_length,
                    'numeric_columns_found': len(numeric_columns),
                    'date_range': {
                        'start': df[date_column].min().strftime('%Y-%m-%d'),
                        'end': df[date_column].max().strftime('%Y-%m-%d')
                    }
                }
            }
            
        except Exception as e:
            return {'is_valid': False, 'error': f'Error processing CSV: {str(e)}'}

    def _detect_date_column(self, df: pd.DataFrame) -> str:
        """Detect date column with improved pattern matching and validation"""
        potential_date_columns = []
        
        # First, check for obvious date patterns in column names
        for col in df.columns:
            col_lower = col.lower().strip()
            if any(pattern in col_lower for pattern in self.date_patterns):
                potential_date_columns.append(col)
        
        # If no obvious patterns, check if any column can be converted to datetime
        if not potential_date_columns:
            for col in df.columns:
                try:
                    # Try to convert first few non-null values
                    sample = df[col].dropna().head(10)
                    if len(sample) > 0:
                        converted = pd.to_datetime(sample, errors='coerce')
                        if not converted.isna().all():  # At least some valid dates
                            potential_date_columns.append(col)
                except:
                    continue
        
        # Validate and select best date column
        for col in potential_date_columns:
            try:
                converted = pd.to_datetime(df[col], errors='coerce')
                valid_ratio = converted.notna().sum() / len(df)
                if valid_ratio > 0.8:  # At least 80% valid dates
                    return col
            except:
                continue
        
        # If still no good column found, return the first potential one
        return potential_date_columns[0] if potential_date_columns else None