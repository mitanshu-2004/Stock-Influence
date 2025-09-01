import pandas as pd

class VisualizationEngine:
    def create_correlation_matrix(self, data: pd.DataFrame):
        # Replace NaN with 0 for JSON compatibility
        corr_matrix = data.corr().fillna(0)
        return {
            'type': 'correlation_matrix',
            'data': {
                'columns': corr_matrix.columns.tolist(),
                'values': corr_matrix.values.tolist()
            }
        }

    def create_time_series_data(self, data: pd.DataFrame, date_column: str, variables):
        dates = pd.to_datetime(data[date_column], errors='coerce')
        traces = []
        for var in variables:
            if var in data.columns:
                # Replace NaN with None for JSON compatibility
                y_values = data[var].where(pd.notna(data[var]), None).tolist()
                traces.append({
                    'x': dates.dt.strftime('%Y-%m-%d').tolist(),
                    'y': y_values,
                    'name': var,
                    'type': 'scatter',
                    'mode': 'lines+markers'
                })
        return {
            'type': 'time_series',
            'data': traces
        }