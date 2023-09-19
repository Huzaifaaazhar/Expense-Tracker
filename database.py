import os
from deta import Deta
from dotenv import load_dotenv

#load environment variables.
load_dotenv("G:\Proxima AI\StreamLIT\Expense tracker\.env.txt")
DETA_KEY = os.getenv("DETA_KEY")

#Initialize with project key.
deta = Deta(DETA_KEY)

#Connect to database.
db = deta.Base('stream')

def insert_period(period, incomes, expenses, comment):
    #Return on successful creation, otherwise raisess an error.
    return db.put({'key': period, 'incomes': incomes, 'expenses': expenses, 'comment': comment})

def fetch_all_period():
    #Return dict of all periods.
    res = db.fetch()
    return res.items

def get_period(period):
    #If not found, function will Return none.
    return db.get(period)