def position_size(entry: float, stop: float, risk_budget: float):
    distance=abs(float(entry)-float(stop))
    if distance<=0: return 0,0.0
    qty=max(0,int(float(risk_budget)//distance))
    return qty,qty*distance
