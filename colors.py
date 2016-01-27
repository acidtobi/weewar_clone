colordata = [
    [0, "",  "none"],
    [1, "r", "red"],
    [2, "b", "blue"],
    [3, "y", "yellow"],
    [4, "g", "green"],
    [5, "w", "white"],
    [6, "p", "purple"]
]

class Color(object):
    def __init__(self, id, code, name):
        self.id = id
        self.code = code
        self.name = name

type = [Color(id, code, name) for (id, code, name) in colordata]
code2id = dict((code, id) for (id, code, name) in colordata)

def id_from_code(color_code):
    return code2id[color_code]
