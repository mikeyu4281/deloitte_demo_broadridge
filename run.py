# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 09:49:02 2026

@author: Samsung
"""

import sys
import quickfix as fix
from fix_client import FixClientApp

def main(config_file):
    try:
        settings = fix.SessionSettings(config_file)
        app = FixClientApp()
        storeFactory = fix.FileStoreFactory(settings)
        logFactory = fix.ScreenLogFactory(settings)
        initiator = fix.SocketInitiator(app, storeFactory, settings, logFactory)
        initiator.start()
        print("Initiator started. Press Ctrl+C to stop.")
        # ... wait loop
    except Exception as e:
        print(f"Error: {e}")
    finally:
        initiator.stop()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run.py <config_file>")
        sys.exit(1)
    main(sys.argv[1])