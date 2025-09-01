import pandas as pd
from scipy.stats import pearsonr, spearmanr, kendalltau
from scipy import stats
import numpy as np

class CorrelationAnalyzer:
    methods = {
        'pearson': pearsonr,
        'spearman': spearmanr,
        'kendall': kendalltau
    }

    def analyze_correlations(self, data: pd.DataFrame, numeric_columns, methods=None, min_correlation=0.1):
        if not methods:
            methods = ['pearson']
        correlations = []
        for i, var1 in enumerate(numeric_columns):
            for j, var2 in enumerate(numeric_columns):
                if i < j:
                    clean_data = data[[var1, var2]].dropna()
                    if len(clean_data) < 3 or clean_data[var1].nunique() == 1 or clean_data[var2].nunique() == 1:
                        continue
                    for method in methods:
                        try:
                            corr_func = self.methods[method]
                            corr, p_val = corr_func(clean_data[var1], clean_data[var2])
                            
                            # Calculate confidence interval
                            confidence_interval = self._calculate_confidence_interval(corr, len(clean_data))
                            
                            correlations.append({
                                'variable1': var1,
                                'variable2': var2,
                                'correlation': float(corr),
                                'p_value': float(p_val),
                                'method': method,
                                'n_observations': len(clean_data),
                                'significant': bool(p_val < 0.05),
                                'confidence_interval': confidence_interval
                            })
                        except Exception as e:
                            print(f"Correlation calculation error for {var1} vs {var2}: {str(e)}")
        correlations.sort(key=lambda x: abs(x['correlation']), reverse=True)
        return correlations
    
    def _calculate_confidence_interval(self, correlation, n, confidence_level=0.95):
        """Calculate confidence interval for correlation coefficient using Fisher's z-transform"""
        try:
            if abs(correlation) >= 1.0 or n < 4:
                return None
            
            # Fisher's z-transform
            z = 0.5 * np.log((1 + correlation) / (1 - correlation))
            
            # Standard error
            se = 1 / np.sqrt(n - 3)
            
            # Critical value for given confidence level
            alpha = 1 - confidence_level
            z_critical = stats.norm.ppf(1 - alpha/2)
            
            # Confidence interval in z-space
            z_lower = z - z_critical * se
            z_upper = z + z_critical * se
            
            # Transform back to correlation space
            r_lower = (np.exp(2 * z_lower) - 1) / (np.exp(2 * z_lower) + 1)
            r_upper = (np.exp(2 * z_upper) - 1) / (np.exp(2 * z_upper) + 1)
            
            return {
                'lower': float(r_lower),
                'upper': float(r_upper),
                'confidence_level': confidence_level
            }
        except Exception as e:
            return None