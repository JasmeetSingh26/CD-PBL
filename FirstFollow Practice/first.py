from collections import OrderedDict

# Global variables
t_list = OrderedDict()
nt_list = OrderedDict()
production_list = []

# Terminal symbol class
class Terminal:
    def __init__(self, symbol):
        self.symbol = symbol

    def __str__(self):
        return self.symbol

# Non-terminal symbol class
class NonTerminal:
    def __init__(self, symbol):
        self.symbol = symbol
        self.first = set()
        self.follow = set()

    def __str__(self):
        return self.symbol

    def add_first(self, symbols):
        self.first |= set(symbols)

    def add_follow(self, symbols):
        self.follow |= set(symbols)

# Compute FIRST set for a symbol
def compute_first(symbol):
    global production_list, nt_list, t_list

    if symbol in t_list:
        return set(symbol)

    for prod in production_list:
        head, body = prod.split('->')

        if head != symbol:
            continue

        if body == '':
            nt_list[symbol].add_first('ϵ')
            continue

        for i, Y in enumerate(body):
            if Y == symbol:
                continue

            t = compute_first(Y)
            nt_list[symbol].add_first(t - {'ϵ'})

            if 'ϵ' not in t:
                break

            if i == len(body) - 1:
                nt_list[symbol].add_first('ϵ')

    return nt_list[symbol].first

# Wrapper to get FIRST set
def get_first(symbol):
    return compute_first(symbol)
