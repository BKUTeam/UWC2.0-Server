import os

from dotenv import load_dotenv
from uwc_logging import UwcLogger


class Locals:

    @staticmethod
    def load_config():
        load_dotenv()
        api_type = os.getenv('API_TYPE')
        mapbox_api_key = os.getenv('MAPBOX_API_KEY')
        mcp_filled_threshold = os.getenv('MCP_FILLED_THRESHOLD')
        mcp_filled_threshold_low = os.getenv('MCP_FILLED_THRESHOLD_LOW')
        google_api_key = os.getenv('GOOGLE_API_KEY')
        default_loaded_percent = os.getenv('DEFAULT_LOADED_PERCENT')

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
        else:
            mcp_filled_threshold = int(os.getenv('MCP_FILLED_THRESHOLD'))

        if mcp_filled_threshold_low is None:
            mcp_filled_threshold_low = 20
            UwcLogger.add_info_log(".env", "Using default MCP low filled threshold {}".format(mcp_filled_threshold_low))
        else:
            mcp_filled_threshold_low = int(os.getenv('MCP_FILLED_THRESHOLD_LOW'))

        if default_loaded_percent is None:
            default_loaded_percent = 70
            UwcLogger.add_info_log(".env", "Using default loaded percent {}".format(default_loaded_percent))
        else:
            default_loaded_percent = int(default_loaded_percent)

        return {
            'mcp_filled_threshold': mcp_filled_threshold,
            'mcp_filled_threshold_low': mcp_filled_threshold_low,
            'api_type': api_type,
            'mapbox_api_key': mapbox_api_key,
            'google_api_key': google_api_key,
            'default_loaded_percent': default_loaded_percent
        }
