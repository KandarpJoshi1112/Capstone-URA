# main.py
import argparse
import os
import sys
import time
from utils.logger import setup_logger
from agent.orchestrator import Orchestrator



DEFAULT_CONFIG_PATH = "config/settings.json"

def parse_args():
    parser = argparse.ArgumentParser(description="Unified Reality Agent (URA) - runner")
    parser.add_argument("--config", type=str, default=DEFAULT_CONFIG_PATH, help="Path to settings.json")
    parser.add_argument("--mode", type=str, choices=["demo", "real"], help="Override mode (demo/real)")
    parser.add_argument("--location", type=str, default="Rajkot", help="Location for weather query demo")
    return parser.parse_args()

def pretty_print_weather(data: dict):
    print("\n" + "-"*41)
    print(f"           WEATHER REPORT ({data.get('source','').upper()} MODE)")
    print("-"*41)

    print(f"Location     : {data.get('location')}")
    print(f"Timestamp    : {data.get('timestamp')}\n")

    print(f"Temperature  : {data.get('temperature_c')} °C")
    print(f"Humidity     : {data.get('humidity')} %")
    print(f"Wind Speed   : {data.get('wind_kmph')} km/h")
    print(f"Summary      : {data.get('summary')}\n")

    print("-"*41)
    print(f"Source       : {data.get('source').upper()}")
    print("-"*41 + "\n")


def main():
    args = parse_args()

    # Initialize a bootstrap logger so early messages get printed
    bootstrap_logger = setup_logger("ura-bootstrap", None)
    try:
        orchestrator = Orchestrator(config_path=args.config, cli_mode=args.mode)

        # Demo: fetch weather and print result (this is the program's simple demo loop)
        bootstrap_logger.info("Starting URA main loop in mode=%s", orchestrator.mode)

        # Example single run - in production this would be an API server or event-driven
        result = orchestrator.fetch_weather(args.location)
        bootstrap_logger.info("Fetched weather: %s", result)
        
        #print(result)
        pretty_print_weather(result)

        # Sleep briefly to keep the watcher active for manual edits if user wants to change config
        bootstrap_logger.info("Main completed. Keeping process alive for 5s to allow config hot-reload demo.")
        time.sleep(5)

    except Exception as e:
        bootstrap_logger.exception("Fatal error in URA: %s", e)
        sys.exit(2)
    finally:
        try:
            orchestrator.stop()
        except Exception:
            pass

if __name__ == "__main__":
    main()
