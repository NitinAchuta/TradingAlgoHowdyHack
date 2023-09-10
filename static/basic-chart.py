import pandas as pd 
import matplotlib
import yfinance as yf
import math

##
## PRINT COMPANY INFO
##
def print_field(field_name, field_value):
    if field_value != 'N/A':
        print(f"{field_name}: {field_value}")

def get_company_info(ticker_symbol):
    try:
        # Create a Ticker object for the specified company
        ticker = yf.Ticker(ticker_symbol)

        # Get information about the company
        company_info = ticker.info

        # Extract and print the requested information
        print_field("Company Name", company_info.get('longName', 'N/A'))
        
        # Check if CEO information is directly available
        ceo = company_info.get('ceo', 'N/A')
        if ceo == 'N/A':
            # If not, try to extract it from the management field
            management = company_info.get('management', [{'title': 'N/A', 'name': 'N/A'}])
            ceo = next((item['name'] for item in management if item['title'] == 'CEO'), 'N/A')
        
        if ceo != 'N/A':
            print_field("CEO", ceo)
        else:
            print("The CEO of this company was not listed directly under Yahoo Finance")
        
        print_field("Founding Year", company_info.get('founded', 'N/A'))
        location = company_info.get('city', 'N/A') + ', ' + company_info.get('state', 'N/A')
        print_field("Location", location)
        print_field("Types of Products", company_info.get('industry', 'N/A'))
        print_field("Primary Function", company_info.get('sector', 'N/A'))
        print_field("Full time employees", company_info.get('fullTimeEmployees', 'N/A'))

    except yf.TickerError as te:
        print(f"Error fetching data for {ticker_symbol}: {te}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

##
##PRINT BUY/SELL BASED ON MAs
##
def MA_Signal():
    # Gets the ticker
    ticker = yf.Ticker(PermTicker)

    # Gets the value of the stock for the past 5 years 
    data = ticker.history(period='5y')

    # Drops all the data that we don't need 
    data.drop(["Volume", "Dividends", "Stock Splits"], inplace=True, axis=1)

    # Gets the 20 and 200 Moving Averages
    data['20MA'] = data['Close'].rolling(20).mean()
    data['100MA'] = data['Close'].rolling(100).mean()

    data.dropna(inplace=True)

    cross_points = []

    global finalStrength

    for i in range(1, len(data)):
        if data['20MA'].iloc[i] > data['100MA'].iloc[i] and data['20MA'].iloc[i - 1] < data['100MA'].iloc[i - 1]:
            cross_points.append((data.index[i], '20MA crosses above 100MA so it was good to buy'))
            crossTypeUp = True
        elif data['20MA'].iloc[i] < data['100MA'].iloc[i] and data['20MA'].iloc[i - 1] > data['100MA'].iloc[i - 1]:
            cross_points.append((data.index[i], '20MA crosses below 100MA so it was good to short'))
            crossTypeUp = False

    for date, cross_type in cross_points:
        formatted_date = date.date()
        if crossTypeUp == True:
            finalStrength = True
        else:
            finalStrength = False
 

#Finally displaying historical buys and sells for the last 5 years
#
#Also holds the most recent signal in the global finalStrength variable


# Call the function to get information for multiple companies

global ticker
ticker = input("Enter the TICKER(not the actual name) of the company: ")
PermTicker = ticker

#Getting the basic info of the company
get_company_info(ticker)

#Getting the signal of the company based on the 100 and 20 MAs
MA_Signal()

signal = None
if finalStrength == True:
    signal = True
else:
    signal = False

print(f'This is a {signal} signal')

in_tickstr = str(PermTicker)

in_tick = yf.Ticker(PermTicker)

PE = int(in_tick.info['forwardPE'])
PWeight = 0

#Calculates and assignes a Variable baesd on P/E favorability
if(PE>30):
    ##high price/ earnings
    if(100-PE>30):
        #So ass
        Pweight = .2
    else:
        #eh
        Pweight = .5
else:
    ##low price to earnings (favorable)
    Pweight = 1

#Calculates Rate of Dividend and assignes value based on Favorability
#Analyst Recomendations

recomend = str((in_tick.info['recommendationKey']))
buy = 'buy'
if(recomend == buy):
    Wrec = 1
else:
    Wrec = .3

#Analyst predicted end of year close vs Current Close

targetp = float(in_tick.info['targetMeanPrice'])

close = float(in_tick.info['previousClose'])
Wchange= 0


if(targetp > close):
    #Stock Should be bullish in long term
    if(((targetp-close)/close)*100 > 14):
        #Very Bullish
        Wchange = 1
    elif(((targetp-close)/close)*100 >  7):
        #Decently Bullish
        Wchange = 0.7
    else:
        Wchange = 0.6
else:
    #Do not buy this shit
    Wchange = 0.1

sector = str(in_tick.info['sector'])
tech = 'Technology'

margin = float(in_tick.info['ebitdaMargins'])

if(sector == tech):
    if(margin > .20):
        #REALLY FUCKING GOOD BUY
        Wmargin = 1.0
    elif(margin>.10):
        #aight
        Wmargin = 0.7
else:
    if(margin > .10):
        #goood
        Wmargin = 0.8
    elif(margin > 0.08):
        #this company a lil off
        Wmargin = 0.6
    elif(margin<0):
        #HELL NAH THIS NEGATIVE DAWG SELL
        Wmargin = 0.1

strengthindic = (Pweight*100*0.15)  + (Wrec*100*0.20) + (Wchange* 100* 0.28) + (Wmargin *100 * .37)
print(f'The strength of this ticker is {strengthindic}')

#90 or above is strong buy
#80-90 medium buy
#<80 weak buy
if(strengthindic>=90 and finalStrength ):
    print('Based on strong fundamental analysis combined with the 100MA and 20MA crossing in a bullish pattern, this ticker will return strong profits in the future. Indications such as strong profit margins and postitive predictions from Wall Street Market Analysts there is a high probability of an uptrend in the future.')
elif(strengthindic>=80 and finalStrength):
    print('Based on fundamental analysis combined with the 100MA and 20MA crossing in a bullish and crabish pattern, this ticker will return profits in the future. Supported by earnings analysis, this ticker has a decent shot of being profitable in the future due to strong profits and good ratings by Wall Street Investors.')
elif(strengthindic>=70 and finalStrength):
    print('Based on fundamental analysis combined with the 100MA and 20MA crossing in a slightly bullish, mostly crabbish pattern, calculations indicate that this ticker has a small chance of positive returns in the future. Analysts give mixed reports on this ticker and caution is advised.')
elif(finalStrength or strengthindic >= 70):
    print('Based on fundamental analysis combined with the 100MA and 20MA crossing in a slightly bullish, mostly crabbish pattern, calculations indicate that this ticker has a small chance of positive returns in the future(in its current state). Wall Street Analysts give mixed reports on this ticker and caution is advised. However, pure techinicals show the exact opposite of what analysts say. With this split between technicals and analyst opinions, heavy caution is advised as it could mean a massive movement in either direction')
else:
    print('Based on fundamental analysis combined with the 100MA and 20MA crossing in a very bearish pattern, there is a close to 0 percent chance that this ticker will have positive returns in the near future. Analysts give sell reports on this ticker and heavily caution investors to keep away form this stock in its current state.')