#using python version 3.12.0
#using pandas 2.1.4
import pandas as pd
import dateutil.parser as parser
import numpy as np

#read from csv
df = pd.read_csv("bank.csv")

#drop Ref Num and Account Number
df.drop("Ref Num", axis=1, inplace=True)
df.drop("Account Number", axis=1, inplace=True)

#create datetime, there are some ambiguous data, used dateutil library to parse it
df["datetime"] = df["Date"].apply(lambda x: parser.parse(x).strftime('%Y-%m-%dT%H:%M:%SZ'))
df.drop("Date", axis=1, inplace=True)

#rename currency
df["currency"] = df["Currency"]
df.drop("Currency", axis=1, inplace=True)

#create amount
df = df.replace("[\$,]", '', regex=True)
df["amount"] = df["CR Amount"].astype(float) + df["DB Amount"].astype(float)

#create type, there are no anamoly data so I can decide type based on one of the CR or DB amount
df["type"] = np.where(df["CR Amount"].astype(float) == 0.00, 'TRANSFER OUT', 'TRANSFER IN')
df.drop("CR Amount", axis=1, inplace=True)
df.drop("DB Amount", axis=1, inplace=True)

print(df.datetime)
print(df.head())

df.to_csv("data1.csv", index=False)


