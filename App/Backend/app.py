from flask import Flask, request, jsonify, render_template
from collections import OrderedDict
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

t_list = OrderedDict()
nt_list = OrderedDict()
production_list = []

class Terminal:
    def __init__(self, symbol):
        self.symbol = symbol
    def __str__(self):
        return self.symbol

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

class Item(str):
    def __new__(cls, item, lookahead=list()):
        obj = str.__new__(cls, item)
        obj.lookahead = lookahead
        return obj
    def __str__(self):
        return super(Item, self).__str__() + ", " + '|'.join(self.lookahead)

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

def get_first(symbol):
    return compute_first(symbol)

def compute_follow(symbol):
    global production_list, nt_list
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

def get_follow(symbol):
    if symbol in t_list:
        return None
    return nt_list[symbol].follow

def reset_globals():
    global t_list, nt_list, production_list
    t_list = OrderedDict()
    nt_list = OrderedDict()
    production_list = []

def closure(items):
    def exists(newitem, items):
        for i in items:
            if i == newitem and sorted(set(i.lookahead)) == sorted(set(newitem.lookahead)):
                return True
        return False

    global production_list

    while True:
        flag = 0
        for i in items:
            if i.index('.') == len(i) - 1: 
                continue

            Y = i.split('->')[1].split('.')[1][0]

            if i.index('.') + 1 < len(i) - 1:
                lastr = list(compute_first(i[i.index('.') + 2]) - set(['ϵ']))
            else:
                lastr = i.lookahead

            for prod in production_list:
                head, body = prod.split('->')
                if head != Y: 
                    continue

                newitem = Item(Y + '->.' + body, lastr)
                if not exists(newitem, items):
                    items.append(newitem)
                    flag = 1
        if flag == 0:
            break
    return items

def goto(items, symbol):
    global production_list
    initial = []

    for i in items:
        if i.index('.') == len(i) - 1: 
            continue

        head, body = i.split('->')
        seen, unseen = body.split('.')

        if unseen[0] == symbol and len(unseen) >= 1:
            initial.append(Item(head + '->' + seen + unseen[0] + '.' + unseen[1:], i.lookahead))

    return closure(initial)

def calc_states():
    def contains(states, t):
        for s in states:
            if len(s) != len(t): 
                continue
            if sorted(s) == sorted(t):
                for i in range(len(s)):
                    if s[i].lookahead != t[i].lookahead:
                        break
                else:
                    return True
        return False

    global production_list

    head, body = production_list[0].split('->')
    states = [closure([Item(head + '->.' + body, ['$'])])]

    while True:
        flag = 0
        for s in states:
            for e in list(nt_list.keys()) + list(t_list.keys()):
                t = goto(s, e)
                if t == [] or contains(states, t):
                    continue
                states.append(t)
                flag = 1
        if not flag:
            break

    return states

def augment_grammar():
    global production_list, nt_list
    for i in range(ord('Z'), ord('A') - 1, -1):
        if chr(i) not in nt_list:
            start_prod = production_list[0]
            production_list.insert(0, chr(i) + '->' + start_prod.split('->')[0])
            return

def build_parsing_table(states):
    table = []
    symbols = list(t_list.keys()) + list(nt_list.keys()) + ['$']
    state_map = {tuple(sorted(str(item) for item in s)): idx for idx, s in enumerate(states)}

    for idx, state in enumerate(states):
        row = {sym: '' for sym in symbols}
        for item in state:
            if item.index('.') == len(item) - 1:
                head, body = item.split('->')
                body = body.replace('.', '')
                if head == production_list[0].split('->')[0] and body == production_list[1].split('->')[0]:
                    row['$'] = 'Accept'
                else:
                    prod_no = production_list.index(f"{head}->{body}")
                    for la in item.lookahead:
                        row[la] = f"r{prod_no}"
            else:
                after_dot = item.split('->')[1].split('.')[1]
                next_symbol = after_dot[0]
                next_state = goto(state, next_symbol)
                for k, v in state_map.items():
                    if sorted(k) == sorted(str(x) for x in next_state):
                        if next_symbol in t_list:
                            row[next_symbol] = f"s{v}"
                        elif next_symbol in nt_list:
                            row[next_symbol] = str(v)
        table.append(row)
    return table

#@app.route('/')
#def index():
#    return render_template('index.html')

@app.route('/compute', methods=['POST'])
def compute():
    reset_globals()
    data = request.json
    grammar = data.get('grammar', '')
    lines = grammar.strip().split('\n')

    for line in lines:
        line = line.strip().replace(' ', '')
        if line == '':
            continue
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

    for nt in nt_list:
        compute_first(nt)
    for nt in nt_list:
        compute_follow(nt)

    augment_grammar()
    states = calc_states()
    table = build_parsing_table(states)

    first_result = {nt: sorted(list(nt_list[nt].first)) for nt in nt_list}
    follow_result = {nt: sorted(list(nt_list[nt].follow)) for nt in nt_list}
    states_str_list = []
    for idx, state in enumerate(states):
        state_lines = [f"Item {idx}:"]
        for item in state:
            lookahead = "|".join(item.lookahead)
            state_lines.append(f"  {str(item)} , {lookahead}")
        states_str_list.append("\n".join(state_lines))

    # Convert parsing table to a string
    table_str = []
    header = ['State'] + list(t_list.keys()) + ['$'] + list(nt_list.keys())
    table_str.append('\t'.join(header))
    for idx, row in enumerate(table):
        row_str = [str(idx)] + [row.get(sym, '') for sym in header[1:]]
        table_str.append('\t'.join(row_str))

    return jsonify({
        'FIRST': first_result,
        'FOLLOW': follow_result,
        'STATES': "\n\n".join(states_str_list),
        'TABLE': "\n".join(table_str)
    })

# LL(1) Parser Implementation
def compute_ll1_table():
    table = {}
    for nt in nt_list:
        table[nt] = {}
        for t in list(t_list.keys()) + ['$']:
            table[nt][t] = ''

    for prod in production_list:
        head, body = prod.split('->')
        first_of_body = set()
        
        if body == '':  # Empty production
            first_of_body = {'ϵ'}
        else:
            # Calculate FIRST of the body
            has_epsilon = True
            for symbol in body:
                if not has_epsilon:
                    break
                if symbol in t_list:
                    first_of_body.add(symbol)
                    has_epsilon = False
                else:
                    symbol_first = nt_list[symbol].first
                    first_of_body |= symbol_first - {'ϵ'}
                    if 'ϵ' not in symbol_first:
                        has_epsilon = False
            if has_epsilon:
                first_of_body.add('ϵ')

        # For each terminal in FIRST(body), add the production to the table
        for terminal in first_of_body - {'ϵ'}:
            if table[head][terminal]:
                return None, f"Grammar is not LL(1): Conflict at {head}, {terminal}"
            table[head][terminal] = prod

        # If ϵ is in FIRST(body), add the production to FOLLOW(head)
        if 'ϵ' in first_of_body:
            for terminal in nt_list[head].follow:
                if table[head][terminal]:
                    return None, f"Grammar is not LL(1): Conflict at {head}, {terminal}"
                table[head][terminal] = prod

    return table, None

@app.route('/compute_ll1', methods=['POST'])
def compute_ll1():
    reset_globals()
    data = request.json
    grammar = data.get('grammar', '')
    lines = grammar.strip().split('\n')

    for line in lines:
        line = line.strip().replace(' ', '')
        if line == '':
            continue
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

    # Compute FIRST and FOLLOW sets
    for nt in nt_list:
        compute_first(nt)
    for nt in nt_list:
        compute_follow(nt)

    # Compute LL(1) parsing table
    parsing_table, error = compute_ll1_table()
    
    if error:
        return jsonify({
            'error': error
        }), 400

    # Convert parsing table to string format
    table_str = []
    terminals = list(t_list.keys()) + ['$']
    header = ['Non-Terminal'] + terminals
    table_str.append('\t'.join(header))
    
    for nt in nt_list:
        row = [nt] + [parsing_table[nt][t] for t in terminals]
        table_str.append('\t'.join(row))

    first_result = {nt: sorted(list(nt_list[nt].first)) for nt in nt_list}
    follow_result = {nt: sorted(list(nt_list[nt].follow)) for nt in nt_list}

    return jsonify({
        'FIRST': first_result,
        'FOLLOW': follow_result,
        'TABLE': '\n'.join(table_str)
    })

if __name__ == '__main__':
    app.run(port=5000, debug=True)