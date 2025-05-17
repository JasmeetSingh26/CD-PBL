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
# if X is a terminal then first(X) = X
    if symbol in t_list:
        return set(symbol)

    for prod in production_list:
        head, body = prod.split('->')

        if head != symbol:
            continue
# if X -> is a production, then first(X) = epsilon
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

# Compute FOLLOW set
def compute_follow(symbol):
    global production_list, nt_list
# if A is the start symbol, follow (A) = $
    if symbol == list(nt_list.keys())[0]:
        nt_list[symbol].add_follow('$')

    for prod in production_list:
        head, body = prod.split('->')

        for i, B in enumerate(body):
            if B != symbol:
                continue

            if i != len(body) - 1:
                next_symbol = body[i + 1]
                nt_list[symbol].add_follow(get_first(next_symbol) - {'ϵ'})

            if i == len(body) - 1 or ('ϵ' in get_first(body[i + 1]) and B != head):
                nt_list[symbol].add_follow(get_follow(head))

# Wrapper to get FOLLOW set
def get_follow(symbol):
    if symbol in t_list:
        return None
    return nt_list[symbol].follow

# Input grammar and compute results
def main():
    global production_list, t_list, nt_list

    print("Enter the grammar productions (enter 'end' or blank line to finish):")
    print("Format: A->aB or A-> (for epsilon)")

    while True:
        line = input().strip().replace(' ', '')
        if line.lower() == 'end' or line == '':
            break
        production_list.append(line)

        head, body = line.split('->')

        if head not in nt_list:
            nt_list[head] = NonTerminal(head)

        for symbol in body:
            if not symbol.isupper():
                if symbol not in t_list:
                    t_list[symbol] = Terminal(symbol)
            else:
                if symbol not in nt_list:
                    nt_list[symbol] = NonTerminal(symbol)

    
# **************************Testing*******************************
    # # Compute FIRST sets
    # for nt in nt_list:
    #     compute_first(nt)

    # # Compute FOLLOW sets
    # for nt in nt_list:
    #     compute_follow(nt)

    # # Display FIRST sets
    # print("\nFIRST sets:")
    # for nt in nt_list:
    #     first_set = ', '.join(sorted(nt_list[nt].first))
    #     print(f"FIRST({nt}) = {{ {first_set} }}")

    # # Display FOLLOW sets
    # print("\nFOLLOW sets:")
    # for nt in nt_list:
    #     follow_set = ', '.join(sorted(nt_list[nt].follow))
    #     print(f"FOLLOW({nt}) = {{ {follow_set} }}")
# ********************************************************************

# Run main
if __name__ == '__main__':
    main()