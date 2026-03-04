# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 15:58:48 2026

@author: Samsung
"""

import json
from flask import Flask, request, jsonify
from datetime import datetime

# --- Fallback FIX string builder (if QuickFIX is not available) ---
def build_fix_message_fallback(params):
    """
    Build a simple FIX 4.4 NewOrderSingle string from input parameters.
    This is a minimal example – real messages need many more tags.
    """
    fix_version = "FIX.4.4"
    msg_type = "D"  # NewOrderSingle
    sending_time = datetime.utcnow().strftime("%Y%m%d-%H:%M:%S.%f")[:-3]

    # Required fields (example values)
    cl_ord_id = params.get("cl_ord_id", "12345")
    symbol = params.get("symbol", "AAPL")
    side = params.get("side", "1")  # 1 = Buy
    order_qty = params.get("order_qty", "1")
    ord_type = params.get("ord_type", "2")  # 2 = Limit
    price = params.get("price", "150.00")
    option_type = params.get("option_type", "C")  # C = Call, P = Put
    strike = params.get("strike", "100")
    expiry = params.get("expiry", "20260304")  # YYYYMMDD

    # Build FIX tag=value pairs (simplified)
    fix_string = (
        f"8={fix_version}|9=000|35={msg_type}|34=1|49=SENDER|52={sending_time}|56=TARGET|"
        f"11={cl_ord_id}|55={symbol}|54={side}|38={order_qty}|40={ord_type}|"
        f"44={price}|167=OPT|201={option_type}|202={strike}|200={expiry}|"
        f"10=000|"
    )
    # Body length (tag 9) and checksum (tag 10) would need calculation in a real system
    return fix_string

# --- QuickFIX version (if you have QuickFIX installed) ---
def build_fix_message_quickfix(params):
    """
    Build a NewOrderSingle using QuickFIX. Assumes QuickFIX is installed.
    """
    import quickfix as fix
    import quickfix44 as fix44

    # Create the order message
    order = fix44.NewOrderSingle(
        fix.ClOrdID(params.get("cl_ord_id", "12345")),
        fix.Symbol(params.get("symbol", "AAPL")),
        fix.Side(fix.Side_BUY if params.get("side") == "1" else fix.Side_SELL),
        fix.TransactTime(),
        fix.OrdType(fix.OrdType_LIMIT if params.get("ord_type") == "2" else fix.OrdType_MARKET)
    )

    # Set optional fields
    order.setField(fix.OrderQty(float(params.get("order_qty", 1))))
    order.setField(fix.Price(float(params.get("price", 150.00))))

    # Option-specific fields (FIX 4.4 tags)
    order.setField(fix.SecurityType("OPT"))
    order.setField(fix.PutOrCall(1 if params.get("option_type") == "C" else 2))  # 1=Call, 2=Put
    order.setField(fix.StrikePrice(float(params.get("strike", 100))))
    order.setField(fix.MaturityDate(params.get("expiry", "20260304")))

    # Convert to raw string (simulate sending)
    # In a real app you'd use Session.sendToTarget()
    return order.toString()

# Decide which builder to use
try:
    import quickfix
    build_fix_message = build_fix_message_quickfix
except ImportError:
    build_fix_message = build_fix_message_fallback
    print("QuickFIX not installed – using fallback string builder.")

# --- Flask API ---
app = Flask(__name__)

@app.route('/generate_fix', methods=['POST'])
def generate_fix():
    """
    Endpoint that accepts JSON with option data and returns a FIX message.
    Expected JSON keys: symbol, side, order_qty, ord_type, price,
                        option_type (C/P), strike, expiry (YYYYMMDD)
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    # Build the FIX message
    fix_msg = build_fix_message(data)

    return jsonify({
        "fix_message": fix_msg,
        "format": "FIX.4.4",
        "note": "This is a mock API – checksum and body length not computed."
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)