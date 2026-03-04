# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 09:03:57 2026

@author: Samsung
"""

import quickfix as fix
import quickfix44 as fix44
import time
import tbricks_output as tbricks_order

# --- 1. Define your FIX Application ---
class MyFIXInitiator(fix.Application):
    def onCreate(self, sessionID):
        print(f"onCreate: Session created ({sessionID.toString()})")
        return

    def onLogon(self, sessionID):
        print(f"onLogon: Successfully logged on ({sessionID.toString()})")
        # Store the session ID when logged on so we can send messages
        self.sessionID = sessionID
        return

    def onLogout(self, sessionID):
        print(f"onLogout: Session logged out ({sessionID.toString()})")
        return

    def toAdmin(self, message, sessionID):
        # Called before sending admin messages (like Logon).
        # You can customize the Logon message here if needed.
        msg_type = fix.MsgType()
        message.getHeader().getField(msg_type)
        if msg_type.getValue() == fix.MsgType_Logon:
            print("toAdmin: Sending Logon message")
        return

    def fromAdmin(self, message, sessionID):
        # Called when receiving admin messages.
        return

    def toApp(self, message, sessionID):
        # Called before sending application messages (like NewOrderSingle).
        pass

    def fromApp(self, message, sessionID):
        # Called when receiving application messages (like ExecutionReport).
        msg_type = fix.MsgType()
        message.getHeader().getField(msg_type)
        if msg_type.getValue() == fix.MsgType_ExecutionReport:
            print("fromApp: Received Execution Report")
            # You can parse the report here
            # e.g., order_id = fix.ClOrdID(); message.getField(order_id)
        return

# --- 2. Main execution ---
if __name__ == "__main__":
    # Path to your FIX configuration file
    config_file = "initiator.cfg"

    try:
        # Load settings
        settings = fix.SessionSettings(config_file)

        # Create application and factories
        application = MyFIXInitiator()
        storeFactory = fix.FileStoreFactory(settings)
        logFactory = fix.ScreenLogFactory(settings) # Logs to screen for debugging

        # Create and start the initiator
        initiator = fix.SocketInitiator(application, storeFactory, settings, logFactory)
        initiator.start()

        print("Initiator started. Waiting for logon...")
        time.sleep(5) # Give it a moment to log on

        # --- Example: Sending a New Order Single ---
        if hasattr(application, 'sessionID'):
            print("Sending a New Order Single...")
            
            # Create a FIX 4.4 NewOrderSingle message

            #mock order details and uses a basic order object provided by fix44 api
            order = fix44.NewOrderSingle()
            order.setField(fix.ClOrdID("AAPL_Order"))
            order.setField(fix.Symbol("AAPL"))
            order.setField(fix.Side(fix.Side_BUY))
            order.setField(fix.OrdType(fix.OrdType_LIMIT))
            order.setField(fix.Price(150.00))
            order.setField(fix.OrderQty(100))
            order.setField(fix.TimeInForce(fix.TimeInForce_DAY))
            
            # Set the required header fields
            order.getHeader().setField(fix.BeginString("FIX.4.4"))
            order.getHeader().setField(fix.MsgType(fix.MsgType_OrderSingle))
            tbricks_order = tbricks_order.Order
            # order details would populate the tbricks_order object and be sent to exchange
            # Send the message
            fix.Session.sendToTarget(tbricks_order, application.sessionID)
            print("Order sent.")
        else:
            print("Not logged on yet. Cannot send order.")

        # Keep the script running to receive responses
        print("Waiting for responses. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)

    except fix.ConfigError as e:
        print(f"Configuration error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'initiator' in locals():
            initiator.stop()

            print("Initiator stopped.")
