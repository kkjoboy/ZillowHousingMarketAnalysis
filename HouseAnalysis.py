# Author: Joshua Mielke
#

import csv

##########################################################################################################################
# Post-Processing & Data Loading Data Dictionaries, used for calculating ranks
# Ranking Data Dictionaries, lowest aggregate number is highest rank
#
# Should be a dictionary of dictionaries, keys being zip codes and values being another dictionary of different values
# such as '3MonthMovingAverageRent' : 1253 | 'RentHomePricePercent' : 1.2 | 'RentGrowthMovingAverage' : 3.5
# 
# Ranking values include:
#   1. AverageRent                  - Average rent from 3 month moving average
#                                   NOTE: This is the value of the latest ZRI
#   2. OnePercentRule               - TODO Used for calculating rent divided by total cost of house
#   3. RentGrowth                   - 3 month moving average of rent growth
#   4. PriceAppreciation            - TODO 3 month moving average of price appreciation based on ZHVI home values
#   5. PriceAppreciationSqft        - TODO 3 month moving average of price appreciation by square footage
#   6. PctPriceCuts                 - TODO Percent of SFRs that have cuts in price (high = less desirable, low = more desirable)
#   7. AverageHomeValue             - Average home value from ZHVI
##########################################################################################################################
ComputedData = {}
ZipCodeRankings = {}
Header = []

# Global Data Stores (Note: Uses lots of memory to hold global arrays of the excel file)
rentPriceData = {}
housePriceData = {}
priceAdjustmentData = {}

# Filters
RentHomePricePercent = 1.0

##########################################################################################################################
# ZRI Time Series SFR ($) - Zillow [Rental Values]
#
# The Zillow Rent Index (ZRI) is a smooth measure of the median estimated market rate rent across a given region and
# housing type. This value will be used in conjuction with the Median Rent List Price to calculate a median rental rate
# across a given Zip Code. The median rental rate will be used with the median home value to calculate a rank based on
# ratio of rent to home value.
##########################################################################################################################

# Loads the ZRI Rental Prices for Single Family Residences (SFR) data from Zillow
def loadZRIRentalPriceSFRZillow():

    # Open ZRI Rental Prices for Single Family Residences by Zip Code
    with open ('Zip_Zri_SingleFamilyResidenceRental.csv', newline='', encoding='utf-8') as ZRIRentalPriceSFRCSV:

        # Create the CSV reader to collect excel information
        ZRIRentalPriceReader = csv.reader(ZRIRentalPriceSFRCSV, delimiter=',')

        header = next(ZRIRentalPriceReader)
        for headerVal in header:
            Header.append(headerVal)

        # Loop through values in the CSV, starting at index 1 (skip header)
        for row in ZRIRentalPriceReader:
            timeSeriesHeader = []
            timeSeriesPrices = []
            # Loop through each row  
            for x, value in enumerate(row, start=0):
                if x > 6:
                    timeSeriesHeader.append(header[x])
                    timeSeriesPrices.append(value)

            rentPriceData[row[1]] = [row[2], row[3], row[4], row[5], row[6], timeSeriesHeader, timeSeriesPrices]

def loadAverageRent():
    # Grab each zip code and load average rent into computed data
    for row in rentPriceData:

        # Check to make sure if Zip Code already exists in Computed Data, otherwise add it
        # TODO Change the ordering to use a hashmap from header to ensure correct matching from different headers
        if row not in ComputedData:
            ComputedData[row] = {}
            ComputedData[row][Header[2]] = rentPriceData[row][0]  # City
            ComputedData[row][Header[3]] = rentPriceData[row][1]  # State
            ComputedData[row][Header[4]] = rentPriceData[row][2]  # Metro
            ComputedData[row][Header[5]] = rentPriceData[row][3]  # County
            ComputedData[row][Header[6]] = rentPriceData[row][4]  # Size Rank

        # Grab last rent value in timeSeriesPrices (ZRI already calculates 3 month moving average for rent) and add to
        # the ComputedData
        rentEntriesLen = len(rentPriceData[row][6])
        ComputedData[row]['AverageRent'] = rentPriceData[row][6][rentEntriesLen-1] # Most Recent Rental Average (3 Month Moving Average)

def loadRentGrowth():
    # Grab each zip code and load average rent into computed data
    for zipcode in rentPriceData:

        # Check to make sure if Zip Code already exists in Computed Data, otherwise add it
        if zipcode not in ComputedData:
            ComputedData[zipcode] = {}
            ComputedData[zipcode][Header[2]] = rentPriceData[zipcode][0]  # City
            ComputedData[zipcode][Header[3]] = rentPriceData[zipcode][1]  # State
            ComputedData[zipcode][Header[4]] = rentPriceData[zipcode][2]  # Metro
            ComputedData[zipcode][Header[5]] = rentPriceData[zipcode][3]  # County
            ComputedData[zipcode][Header[6]] = rentPriceData[zipcode][4]  # Size Rank

        rentGrowthList = []
        first = None
        second = None
        third = None
        prev = None
        # Calculate rent growth from past 5 years of data and store in rentGrowthList
        for rentValue in rentPriceData[zipcode][6][-30:]:
            # Shift values for moving average (3 point moving average)
            first = second
            second = third

            if prev is not None:
                third = (int(rentValue) - prev) / prev * 100

            # None check
            if first is not None and second is not None and third is not None:              
                movingAverage = (first + second + third) / 3 # Calculate moving average with new value
                rentGrowthList.append(movingAverage) # Add new value to moving average list

            prev = int(rentValue) # Store previous value for next iteration

        # Calculate 3 Month Moving Average of rent growth
        rentGrowth = sum(rentGrowthList) / len(rentGrowthList)
        # print(zipcode + ": " + str(rentGrowth))

        # Store average rent growth in ComputedData
        ComputedData[zipcode]['RentGrowth'] = rentGrowth

##########################################################################################################################
# Median List Price ($ Per Square Foot) - Zillow [Rental Values]
##########################################################################################################################

#TBD

##########################################################################################################################
# Median Rent List Price ($ Per Square Foot), Single-Family Residence - Zillow [Rental Listings]
##########################################################################################################################

#TBD

##########################################################################################################################
# ZHVI Single-Family Homes Time Series ($) - Zillow [Home Values]
########################################################################################################################## 

# Loads the ZHVI Home Prices for Single Family Residences (SFR) data from Zillow
def loadZHVIHomePriceSFRZillow():

    # Open ZRI Rental Prices for Single Family Residences by Zip Code
    with open ('Zip_Zhvi_SingleFamilyResidence.csv', newline='', encoding='utf-8') as ZHVIHomePriceSFRCSV:

        # Create the CSV reader to collect excel information
        ZHVIHomePriceReader = csv.reader(ZHVIHomePriceSFRCSV, delimiter=',')

        header = next(ZHVIHomePriceReader)
        #print(header)

        # Loop through values in the CSV, enumerate starting at index 1 (skip header)
        for row in ZHVIHomePriceReader:
            #print(row)

            timeSeriesHeader = []
            timeSeriesPrices = []
            # Loop through each row  
            for x, value in enumerate(row, start=0):
                if x > 6:
                    timeSeriesHeader.append(header[x])
                    timeSeriesPrices.append(value)

            housePriceData[row[1]] = [row[2], row[3], row[4], row[5], row[6], timeSeriesHeader, timeSeriesPrices]

# Gets the average home value for each zip code
def getAverageHomeValue():
    
    for zipcode in housePriceData:

        # Check to see if zipcode is in our ComputedData
        if zipcode not in ComputedData:
            ComputedData[zipcode] = {}
            ComputedData[zipcode][Header[2]] = housePriceData[zipcode][0]  # City
            ComputedData[zipcode][Header[3]] = housePriceData[zipcode][1]  # State
            ComputedData[zipcode][Header[4]] = housePriceData[zipcode][2]  # Metro
            ComputedData[zipcode][Header[5]] = housePriceData[zipcode][3]  # County
            ComputedData[zipcode][Header[6]] = housePriceData[zipcode][4]  # Size Rank

        # Grab last value of house price data and append as the average house value
        # TODO Fix this hacky shit to grab last value
        for value in housePriceData[zipcode][6][-1:]:
            print(zipcode + ": " + value)
            ComputedData[zipcode]['AverageHomeValue'] = value
        

##########################################################################################################################
# Monthly Home Sales (Number, Seasonally Adjusted) - Zillow [Home Listings and Sales]
##########################################################################################################################

#TBD

##########################################################################################################################
# Monthly For-Sale Inventory (Number, Seasonally Adjusted) - Zillow [Home Listings and Sales]
##########################################################################################################################

#TBD

##########################################################################################################################
# New Monthly For-Sale Inventory (Number, Seasonally Adjusted) - Zillow [Home Listings and Sales]
##########################################################################################################################

#TBD

##########################################################################################################################
# Listings With Price Cut - Seasonally Adjusted, SFR (%) - Zillow [Home Listings and Sales]
##########################################################################################################################

# Loads the Listings With Price Cut - Seasonally Adjusted, SFR (%) data from Zillow
def loadZipListingsPriceCutSeasAdjZillow():

    # Open ZRI Rental Prices for Single Family Residences by Zip Code
    with open ('Zip_Listings_PriceCut_SeasAdj_SingleFamilyResidence.csv', newline='', encoding='utf-8') as ListingPriceCutSeasAdjCSV:

        # Create the CSV reader to collect excel information
        ListingPriceCutSeasAdjReader = csv.reader(ListingPriceCutSeasAdjCSV, delimiter=',')

        header = next(ListingPriceCutSeasAdjReader)
        #print(header)

        # Loop through values in the CSV, enumerate starting at index 1 (skip header)
        for row in ListingPriceCutSeasAdjReader:
            #print(row)

            timeSeriesHeader = []
            timeSeriesPrices = []
            # Loop through each row  
            for x, value in enumerate(row, start=0):
                if x > 6:
                    timeSeriesHeader.append(header[x])
                    timeSeriesPrices.append(value)

            housePriceData[row[1]] = [row[2], row[3], row[4], row[5], row[6], timeSeriesHeader, timeSeriesPrices]

##########################################################################################################################
# Main Function
##########################################################################################################################

def main():
    # Load different spreadsheets
    loadZRIRentalPriceSFRZillow()
    loadZHVIHomePriceSFRZillow()

    # Use rentPriceData to add average rent to computed data
    loadAverageRent()

    # Use rentPriceData to add rent growth to computed data
    loadRentGrowth()

    getAverageHomeValue()

    

if __name__ == "__main__":
    main()