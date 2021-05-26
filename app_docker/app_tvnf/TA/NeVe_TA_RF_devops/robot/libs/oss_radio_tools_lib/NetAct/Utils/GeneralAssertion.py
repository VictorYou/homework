from Utils.Logger import LOGGER


def list_items_should_exist_in_each_other(list_one, alias_one, list_two, alias_two):
    not_in_list_two = []
    not_in_list_one = []
    for item in list_one:
        if item not in list_two:
            not_in_list_two.append(item)
    for item in list_two:
        if item not in list_one:
            not_in_list_one.append(item)

    if not_in_list_one or not_in_list_two:
        if not_in_list_one:
            LOGGER.warn("following items should exist in %s:\n%s"
                        % (alias_one, '\n'.join(not_in_list_one)))
        if not_in_list_two:
            LOGGER.warn("following items should exist in %s:\n%s"
                        % (alias_two, '\n'.join(not_in_list_two)))
        raise AssertionError