import numpy as np

class LeakDetectionEngine:
    def __init__(self, db_manager, ai_gateway):
        self.db = db_manager
        self.ai = ai_gateway

    def run_statistical_cusum(self, item_id: str, baseline_p: float, recent_responses: list) -> bool:
        """
        Calculates Upper CUSUM to detect if an item suddenly became easier.
        """
        # A jump of > 15% in raw passing percentage should be the primary trigger for this specific hackathon demo logic.
        current_p = sum(recent_responses) / len(recent_responses) if recent_responses else baseline_p
        
        # Immediate spike trap (matches our UI logic promise)
        if current_p - baseline_p > 0.15:
            return True
            
        k = 0.5  # allowance slack
        h = 2.0  # control limit threshold
        
        baseline_p = max(min(baseline_p, 0.99), 0.01) # Avoid divide by zero
        
        s = 0
        for is_correct in recent_responses:
            # Shift in standardized performance
            z = (is_correct - baseline_p) / np.sqrt(baseline_p * (1 - baseline_p))
            s = max(0, s + z - k)
            if s > h:
                return True # Alarm!
                
        return False
