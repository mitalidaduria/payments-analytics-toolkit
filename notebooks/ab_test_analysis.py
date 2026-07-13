import numpy as np
import scipy.stats as stats

def analyze_ab_test(control_success, control_total, treatment_success, treatment_total, alpha=0.05):
    """
    Analyzes an A/B test using a two-proportion z-test.
    """
    # 1. Calculate observed conversion rates
    p_control = control_success / control_total
    p_treatment = treatment_success / treatment_total
    observed_diff = p_treatment - p_control
    
    # 2. Pooled proportion under the null hypothesis (no difference)
    p_pooled = (control_success + treatment_success) / (control_total + treatment_total)
    
    # 3. Standard error calculation
    se_pooled = np.sqrt(p_pooled * (1 - p_pooled) * (1/control_total + 1/treatment_total))
    
    # 4. Calculate Z-score and P-value
    z_score = observed_diff / se_pooled
    p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))  # Two-tailed test
    
    # 5. Calculate 95% Confidence Interval for the difference
    se_diff = np.sqrt((p_control * (1 - p_control) / control_total) + 
                      (p_treatment * (1 - p_treatment) / treatment_total))
    z_critical = stats.norm.ppf(1 - alpha/2)
    moe = z_critical * se_diff
    ci_lower = observed_diff - moe
    ci_upper = observed_diff + moe
    
    return {
        "Control Rate": p_control,
        "Treatment Rate": p_treatment,
        "Observed Difference": observed_diff,
        "Z-Score": z_score,
        "P-Value": p_value,
        "Significant": p_value < alpha,
        "95% CI Lower": ci_lower,
        "95% CI Upper": ci_upper
    }

def calculate_sample_size(baseline_rate, mde, power=0.80, alpha=0.05):
    """
    Calculates the required sample size per variant for a given MDE.
    """
    p1 = baseline_rate
    p2 = baseline_rate + mde
    p_bar = (p1 + p2) / 2
    
    z_alpha = stats.norm.ppf(1 - alpha/2)
    z_beta = stats.norm.ppf(power)
    
    # Standard formula for two independent proportions
    numerator = (z_alpha * np.sqrt(2 * p_bar * (1 - p_bar)) + z_beta * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2)))**2
    denominator = (p1 - p2)**2
    
    return int(np.ceil(numerator / denominator))

if __name__ == "__main__":
    print("--- 1. RUNNING A/B TEST SIMULATION ---")
    # Simulation parameters from the roadmap:
    # 10k users each, 97.2% vs 97.8% success rates
    n_control, n_treatment = 10000, 10000
    success_c = int(n_control * 0.972)
    success_t = int(n_treatment * 0.978)
    
    results = analyze_ab_test(success_c, n_control, success_t, n_treatment)
    for key, value in results.items():
        print(f"{key}: {value}")
        
    print("\n--- 2. RUNNING SAMPLE SIZE CALCULATOR ---")
    # What sample size do we need to detect a 0.1% improvement (MDE = 0.001)?
    required_n = calculate_sample_size(baseline_rate=0.972, mde=0.001)
    print(f"Required sample size per variant to detect 0.1% MDE safely: {required_n:,} users")
