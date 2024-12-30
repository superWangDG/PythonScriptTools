from utils.cache_utils import save_to_cache
from localization.localization import get_localized_text


def reset_cache():
    save_to_cache({})
    print(get_localized_text("reset_cache_complete"))
