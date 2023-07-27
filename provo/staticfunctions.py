# from provo.startingpointclasses import Activity, Agent, Entity


def update_dict(dict_old: dict, dict_with_updates: dict) -> dict:
    """updates/adds the fields from dict_with_updates in/to dict_old"""

    for key, value in dict_with_updates.items():
        try:
            value = dict(value)
            value = update_dict(dict_old[key], dict_with_updates=value)
        except:
            dict_old[key] = value
    return dict_old


def get_option(option, sub_option, default_option):
    return option[sub_option] if option.get(sub_option) else default_option
