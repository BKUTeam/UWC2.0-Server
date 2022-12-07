import os

from dotenv import load_dotenv
from uwc_logging import UwcLogger


class Locals:

    @staticmethod
    def load_config():
        load_dotenv()
        api_type = os.getenv('API_TYPE')
        mapbox_api_key = os.getenv('MAPBOX_API_KEY')
        mcp_filled_threshold = int(os.getenv('MCP_FILLED_THRESHOLD'))
        google_api_key = os.getenv('GOOGLE_API_KEY')
        default_loaded_percent = int(os.getenv('DEFAULT_LOADED_PERCENT'))

        if not api_type:
            UwcLogger.add_error_log(".env", "API_TYPE Not found")

        if api_type == 'MAPBOX':
            # UwcLogger.add_info_log(".env", "Using MAPBOX api")
            if mapbox_api_key is None:
                UwcLogger.add_error_log(".env", "MAPBOX_API_KEY Not found")

        elif api_type == 'GOOGLE':
            # UwcLogger.add_info_log(".env", "Using GOOGLE api")
            if google_api_key is None:
                UwcLogger.add_error_log(".env", "GOOGLE_API_KEY Not found")

        if mcp_filled_threshold is None:
            mcp_filled_threshold = 70
            UwcLogger.add_info_log(".env", "Using default MCP filled threshold {}".format(mcp_filled_threshold))

        return {
            'mcp_filled_threshold': mcp_filled_threshold,
            'api_type': api_type,
            'mapbox_api_key': mapbox_api_key,
            'google_api_key': google_api_key,
            'default_loaded_percent': default_loaded_percent
        }
