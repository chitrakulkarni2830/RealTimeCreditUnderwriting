import json
import pandas as pd

def calculate_risk_score(user_id, utility_summary, ecommerce_summary):
    """
    Calculates a weighted risk score (0-100).
    A higher score indicates LOWER RISK (100 is perfect).
    """
    score = 100
    deductions = []
    
    # 1. Utility Deductions (Weighted 60%)
    # Format: "Late: N, Total Billed: $X.XX"
    try:
        late_matches = [int(s) for s in utility_summary.split() if s.isdigit()]
        late_count = late_matches[0] if late_matches else 0
        
        utility_penalty = late_count * 10
        score -= utility_penalty
        if late_count > 0:
            deductions.append(f"Late utility payments (-{utility_penalty})")
    except:
        pass

    # 2. E-commerce Deductions (Weighted 40%)
    try:
        ecom_data = json.loads(ecommerce_summary)
        volatility = ecom_data.get("spending_volatility", 0)
        ratio = ecom_data.get("luxury_vs_essential_ratio", 0)
        
        # Volatility Penalty
        if volatility > 200:
            score -= 15
            deductions.append("High spending volatility (-15)")
        elif volatility > 100:
            score -= 5
            deductions.append("Moderate spending volatility (-5)")
            
        # Luxury Ratio Penalty
        if ratio > 5:
            score -= 20
            deductions.append("Extreme luxury focus (-20)")
        elif ratio > 2:
            score -= 10
            deductions.append("Discretionary spending tilt (-10)")
    except:
        pass

    # Final Bounds
    score = max(0, min(100, score))
    
    # Risk Category
    if score >= 80:
        category = "Tier 1 (Premium)"
    elif score >= 50:
        category = "Tier 2 (Standard)"
    else:
        category = "Tier 3 (Subprime)"
        
    return {
        "score": score,
        "category": category,
        "deductions": deductions
    }
