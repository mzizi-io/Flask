import numpy as np
from numba import jit, njit
import plotly
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import itertools
import json

i = complex(0,1)

'HESTON PRICING'
'==============================='
# To be used in the Heston pricer
@njit
def fHeston(s, St, K, r, T, sigma, kappa, theta, volvol, rho):
    # To be used a lot
    prod = rho * sigma *i *s 
    
    # Calculate d
    d1 = (prod - kappa)**2
    d2 = (sigma**2) * (i*s + s**2)
    d = np.sqrt(d1 + d2)
    
    # Calculate g
    g1 = kappa - prod - d
    g2 = kappa - prod + d
    g = g1/g2
    
    # Calculate first exponential
    exp1 = np.exp(np.log(St) * i *s) * np.exp(i * s* r* T)
    exp2 = 1 - g * np.exp(-d *T)
    exp3 = 1- g
    mainExp1 = exp1 * np.power(exp2/ exp3, -2 * theta * kappa/(sigma **2))
    
    # Calculate second exponential
    exp4 = theta * kappa * T/(sigma **2)
    exp5 = volvol/(sigma **2)
    exp6 = (1 - np.exp(-d * T))/(1 - g * np.exp(-d * T))
    mainExp2 = np.exp((exp4 * g1) + (exp5 *g1 * exp6))
    
    return (mainExp1 * mainExp2)

# Heston Pricer
@njit
def priceHestonMid(St, K, r, T, sigma, kappa, theta, volvol, rho):
    P, iterations, maxNumber = 0,1000,100
    ds = maxNumber/iterations
    
    element1 = 0.5 * (St - K * np.exp(-r * T))
    
    # Calculate the complex integral
    # Using j instead of i to avoid confusion
    for j in range(1, iterations):
        s1 = ds * (2*j + 1)/2
        s2 = s1 - i
        
        numerator1 = fHeston(s2,  St, K, r, T, sigma, kappa, theta, volvol, rho)
        numerator2 = K * fHeston(s1,  St, K, r, T, sigma, kappa, theta, volvol, rho)
        denominator = np.exp(np.log(K) * i * s1) *i *s1
        
        P += ds *(numerator1 - numerator2)/denominator
    
    element2 = P/np.pi
    
    return np.real((element1 + element2))




'PLOTTING FUNCTIONS'
'==============================='
# Create a number of values to change
strikes = np.linspace(3000, 5000, 11)
maturities = np.linspace(0.1, 2, 5)

# Calculate all prices
axes = list(itertools.product(strikes, maturities))
strikeVect = [elem[0] for elem in axes]
maturityVect = [elem[1] for elem in axes]

# Vectorise price calculation
def plots(sigma, kappa, theta, volvol, rho):
    prices = [priceHestonMid(4000, strike, 0.01, maturity, sigma, kappa, theta, volvol, rho)
                    for strike, maturity in zip(strikeVect, maturityVect)]    
    
    prices = np.reshape(prices, (len(strikes), len(maturities)))

    fig = go.Figure(data=[go.Surface(z=prices, 
                                    x=maturities, 
                                    y=strikes,
                                    colorscale = 'solar')])

    # fig['layout']['xaxis']['autorange'] = "reversed"
    fig.layout.template = 'plotly_dark'
    fig.update_layout(title_text='S&P Options Surface (Spot = 4000)', 
                    title_x=0.5,
                    scene = dict(xaxis_title='Maturities',
                                yaxis_title='Strikes',
                                zaxis_title='Prices'),
                    font_color="orange",
                    title_font_color="orange",
                    legend_title_font_color="orange",
                    autosize=False,
                    width=1000, height=700,
                    margin=dict(l=65, r=0, b=65, t=50))

    plotJSON = json.dumps(fig, cls =  plotly.utils.PlotlyJSONEncoder)
    return(plotJSON)


# plots(0.5, 0.2, 0.1, 0.0001, 0.5)