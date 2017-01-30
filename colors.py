def _reduce_list(l, col1, col2):
    return [(x[col1], x[col2]) for x in l]


class Color(object):

    colordata = [
        [0, "",  "none"],
        [1, "r", "red"],
        [2, "b", "blue"],
        [3, "y", "yellow"],
        [4, "g", "green"],
        [5, "w", "white"],
        [6, "p", "purple"]
    ]

    color_id = dict(_reduce_list(colordata, 1, 0) + _reduce_list(colordata, 2, 0))
    color_code = dict(_reduce_list(colordata, 0, 1) + _reduce_list(colordata, 2, 1))
    color_name = dict(_reduce_list(colordata, 0, 2) + _reduce_list(colordata, 1, 2))

    @staticmethod
    def id(key):
        return Color.color_id[key]

    @staticmethod
    def code(key):
        return Color.color_code[key]

    @staticmethod
    def name(key):
        return Color.color_name[key]


