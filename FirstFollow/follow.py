from FirstFollow.first import (
    t_list, nt_list, production_list,
    Terminal, NonTerminal,
    compute_first, get_first
)

# Compute FOLLOW set
def compute_follow(symbol):
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

# Main function to input grammar and compute sets
def main():
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

    # Compute FIRST sets
    for nt in nt_list:
        compute_first(nt)

    # Compute FOLLOW sets
    for nt in nt_list:
        compute_follow(nt)

    # Display FIRST sets
    print("\nFIRST sets:")
    for nt in nt_list:
        first_set = ', '.join(sorted(nt_list[nt].first))
        print(f"FIRST({nt}) = {{ {first_set} }}")

    # Display FOLLOW sets
    print("\nFOLLOW sets:")
    for nt in nt_list:
        follow_set = ', '.join(sorted(nt_list[nt].follow))
        print(f"FOLLOW({nt}) = {{ {follow_set} }}")

# Run main
if __name__ == '__main__':
    main()
