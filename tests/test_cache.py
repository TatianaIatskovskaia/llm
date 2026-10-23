from cache import set_last_pair, get_last_pair, clear_last_pair

def setup_function():
    clear_last_pair()

def test_set_and_get_last_pair():
    set_last_pair("country_from", "country_to")
    assert get_last_pair() == ("country_from", "country_to")

def test_get_last_pair_empty_by_default():
    assert get_last_pair() is None

def test_clear_last_pair():
    set_last_pair("country_from", "country_to")
    clear_last_pair()
    assert get_last_pair() is None

def test_set_last_pair_overwrites_previous():
    set_last_pair("country_from", "country_to")
    set_last_pair("country_from_2", "country_to_2")
    assert get_last_pair() == ("country_from_2", "country_to_2")