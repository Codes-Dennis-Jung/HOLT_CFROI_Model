# pip install numpy-financial
import numpy_financial as npf
import pandas as pd

class HoltCFROIModel:
    def __init__(self):
        """Initialize the Holt CFROI Model calculator"""
        self.inflation_rate = 0.02  # Default inflation rate
        
    def calculate_gross_investment(self, gross_assets, accumulated_depreciation, inflation_adjustment=1.0):
        """Calculate gross investment including inflation adjustments"""
        return (gross_assets - accumulated_depreciation) * inflation_adjustment
    
    def calculate_gross_cash_flow(self, net_income, depreciation, interest_expense, rent_expense):
        """Calculate gross cash flow"""
        return net_income + depreciation + interest_expense * 0.7 + rent_expense  # 0.7 assumes 30% tax rate
    
    def calculate_asset_life(self, gross_assets, depreciation):
        """Estimate remaining asset life"""
        return gross_assets / depreciation if depreciation > 0 else 0
        
    def calculate_cfroi(self, gross_cash_flow, gross_investment, asset_life, fade_rate=0.04):
        """
        Calculate CFROI using iterative IRR calculation
        
        Parameters:
        - gross_cash_flow: Annual gross cash flow
        - gross_investment: Total gross investment
        - asset_life: Estimated asset life in years
        - fade_rate: Rate at which CFROI fades to cost of capital
        
        Returns:
        - CFROI as a decimal or 0.0 if calculation fails
        """
        if asset_life <= 0 or gross_investment <= 0 or gross_cash_flow <= 0:
            return 0.0
            
        try:
            # Create cash flow array
            cash_flows = [-gross_investment]  # Initial investment
            
            # Project cash flows with fade rate
            for year in range(int(asset_life)):
                projected_cf = gross_cash_flow * (1 - fade_rate) ** year
                cash_flows.append(projected_cf)
                
            # Add terminal value
            salvage_value = gross_investment * 0.1  # Assume 10% salvage value
            cash_flows[-1] += salvage_value
            
            # Calculate IRR (CFROI) using numpy_financial
            cfroi = npf.irr(cash_flows)
            
            # Handle case where IRR calculation returns nan
            if pd.isna(cfroi):
                return 0.0
                
            return max(cfroi, 0.0)  # Return 0 if negative IRR
            
        except Exception as e:
            print(f"Error calculating CFROI: {e}")
            return 0.0  # Return 0 instead of None on error
    
    def calculate_economic_profit(self, cfroi, cost_of_capital, gross_investment):
        """Calculate economic profit"""
        if not isinstance(cfroi, (int, float)) or not isinstance(cost_of_capital, (int, float)):
            return 0.0
        return (cfroi - cost_of_capital) * gross_investment
    
    def run_valuation(self, company_data):
        """
        Run full CFROI valuation analysis
        
        Parameters:
        - company_data: dict containing required financial metrics
        
        Returns:
        - dict with CFROI analysis results
        """
        try:
            gross_investment = self.calculate_gross_investment(
                company_data['gross_assets'],
                company_data['accumulated_depreciation'],
                company_data.get('inflation_adjustment', 1.0)
            )
            
            gross_cash_flow = self.calculate_gross_cash_flow(
                company_data['net_income'],
                company_data['depreciation'],
                company_data['interest_expense'],
                company_data['rent_expense']
            )
            
            asset_life = self.calculate_asset_life(
                company_data['gross_assets'],
                company_data['depreciation']
            )
            
            cfroi = self.calculate_cfroi(
                gross_cash_flow,
                gross_investment,
                asset_life,
                company_data.get('fade_rate', 0.04)
            )
            
            economic_profit = self.calculate_economic_profit(
                cfroi,
                company_data.get('cost_of_capital', 0.08),
                gross_investment
            )
            
            return {
                'cfroi': cfroi,
                'economic_profit': economic_profit,
                'gross_investment': gross_investment,
                'gross_cash_flow': gross_cash_flow,
                'asset_life': asset_life
            }
        except Exception as e:
            print(f"Error in valuation calculation: {e}")
            return {
                'cfroi': 0.0,
                'economic_profit': 0.0,
                'gross_investment': 0.0,
                'gross_cash_flow': 0.0,
                'asset_life': 0.0
            }

# Create model instance
model = HoltCFROIModel()

# Example company data with realistic values
company_data = {
    'gross_assets': 10000000,          # $10M in gross assets
    'accumulated_depreciation': 2000000, # $2M accumulated depreciation
    'net_income': 1500000,             # $1.5M net income
    'depreciation': 500000,            # $500K annual depreciation
    'interest_expense': 300000,         # $300K interest expense
    'rent_expense': 200000,            # $200K rent expense
    'cost_of_capital': 0.08,           # 8% cost of capital
    'fade_rate': 0.04                  # 4% fade rate
}

# Run valuation
results = model.run_valuation(company_data)

# Print results with formatting
print("CFROI Analysis Results:")
print(f"CFROI: {results['cfroi']:.2%}")
print(f"Economic Profit: ${results['economic_profit']:,.2f}")
print(f"Gross Investment: ${results['gross_investment']:,.2f}")
print(f"Gross Cash Flow: ${results['gross_cash_flow']:,.2f}")
print(f"Asset Life: {results['asset_life']:.1f} years")