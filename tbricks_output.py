# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 09:17:17 2026

@author: Samsung
"""

# Mapping external JSON to a Tbricks order
import tbricks



external_data = {"ticker": "AAPL", "qty": 100, "price": 175.50}

# Convert to Tbricks object
instrument = tbricks.Instrument.from_symbol(external_data["ticker"])
order = tbricks.LimitOrder(instrument, 
                           tbricks.Side.BUY, 
                           external_data["qty"], 
                           tbricks.Price.from_float(external_data["price"]))

