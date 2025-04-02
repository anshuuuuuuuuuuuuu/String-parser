import streamlit as st
import copy
import pandas as pd



def grammarAugmentation(rules, nonterm_userdef, start_symbol):
    newRules = []
    newChar = start_symbol + "'"
    while newChar in nonterm_userdef:
        newChar += "'"
    newRules.append([newChar, ['.', start_symbol]])
    
    for rule in rules:
        lhs, rhs = rule.split("->")
        lhs = lhs.strip()
        rhs = rhs.strip()
        multirhs = rhs.split('|')
        for rhs1 in multirhs:
            rhs1 = rhs1.strip()
            if rhs1 == '#':
                rhs_split = []
            else:
                rhs_split = rhs1.split()
            rhs_split.insert(0, '.')
            newRules.append([lhs, rhs_split])
    return newRules

def findClosure(input_state, dotSymbol, separatedRulesList, init_start_symbol):
    closureSet = []
    if dotSymbol == init_start_symbol:
        for rule in separatedRulesList:
            if rule[0] == dotSymbol:
                closureSet.append(rule)
    else:
        closureSet = input_state.copy()

    prevLen = -1
    while prevLen != len(closureSet):
        prevLen = len(closureSet)
        tempClosureSet = []
        for rule in closureSet:
            indexOfDot = rule[1].index('.')
            if indexOfDot < len(rule[1]) - 1:
                dotPointsHere = rule[1][indexOfDot + 1]
                for in_rule in separatedRulesList:
                    if dotPointsHere == in_rule[0] and in_rule not in tempClosureSet and in_rule not in closureSet:
                        tempClosureSet.append(in_rule)
        closureSet.extend(tempClosureSet)
    return closureSet

def compute_GOTO(state, statesDict, stateMap, separatedRulesList):
    generateStatesFor = []
    for rule in statesDict[state]:
        indexOfDot = rule[1].index('.')
        if indexOfDot < len(rule[1]) - 1:
            dotPointsHere = rule[1][indexOfDot + 1]
            if dotPointsHere not in generateStatesFor:
                generateStatesFor.append(dotPointsHere)

    for symbol in generateStatesFor:
        GOTO(state, symbol, statesDict, stateMap, separatedRulesList)

def GOTO(state, charNextToDot, statesDict, stateMap, separatedRulesList):
    newState = []
    for rule in statesDict[state]:
        indexOfDot = rule[1].index('.')
        if indexOfDot < len(rule[1]) - 1 and rule[1][indexOfDot + 1] == charNextToDot:
            shiftedRule = copy.deepcopy(rule)
            shiftedRule[1][indexOfDot], shiftedRule[1][indexOfDot + 1] = shiftedRule[1][indexOfDot + 1], shiftedRule[1][indexOfDot]
            newState.append(shiftedRule)

    closure = findClosure(newState, charNextToDot, separatedRulesList, None)
    for item in closure:
        if item not in newState:
            newState.append(item)

    stateExists = -1
    for state_num in statesDict:
        if statesDict[state_num] == newState:
            stateExists = state_num
            break
    if stateExists == -1:
        new_index = max(statesDict.keys()) + 1 if statesDict else 0
        statesDict[new_index] = newState
        stateMap[(state, charNextToDot)] = new_index
    else:
        stateMap[(state, charNextToDot)] = stateExists


def first(rule, diction, term_userdef):
    if not rule:
        return ['#']
    first_symbol = rule[0]
    if first_symbol in term_userdef:
        return [first_symbol]
    elif first_symbol == '#':
        return ['#']
    elif first_symbol in diction:
        fres = []
        for production in diction[first_symbol]:
            prod_first = first(production, diction, term_userdef)
            fres.extend(prod_first)
        if '#' in fres:
            fres.remove('#')
            if len(rule) > 1:
                rest_first = first(rule[1:], diction, term_userdef)
                fres.extend(rest_first)
            else:
                fres.append('#')
        return list(set(fres))
    return []

def follow(nt, diction, start_symbol, term_userdef):
    solset = set()
    if nt == start_symbol:
        solset.add('$')
    for curNT in diction:
        for prod in diction[curNT]:
            for i, symbol in enumerate(prod):
                if symbol == nt:
                    next_pos = i + 1
                    while next_pos <= len(prod):
                        if next_pos == len(prod):
                            if curNT != nt:
                                solset.update(follow(curNT, diction, start_symbol, term_userdef))
                            break
                        next_symbol = prod[next_pos]
                        first_next = first([next_symbol], diction, term_userdef)
                        if '#' in first_next:
                            solset.update([x for x in first_next if x != '#'])
                            next_pos += 1
                        else:
                            solset.update(first_next)
                            break
    return list(solset)


def parse_grammar(grammar_input):
    grammar_rules = {}
    for line in grammar_input.strip().split("\n"):
        parts = line.split(":")
        if len(parts) == 2:
            rule_num = int(parts[0].strip())
            lhs, rhs = parts[1].split("->")
            lhs = lhs.strip()
            rhs = rhs.strip().split()
            
            # Replace epsilon (ε) with #
            rhs = ['#'] if rhs == ["ε"] else rhs  

            grammar_rules[rule_num] = (lhs, rhs)
    return grammar_rules


def generateStates(statesDict, stateMap, separatedRulesList):
    prev_len = -1
    called_GOTO_on = []
    while len(statesDict) != prev_len:
        prev_len = len(statesDict)
        keys = list(statesDict.keys())
        for key in keys:
            if key not in called_GOTO_on:
                called_GOTO_on.append(key)
                compute_GOTO(key, statesDict, stateMap, separatedRulesList)


def generate_conflict_counts(table):
    sr = 0
    rr = 0

    for row in table:
        for cell in row:
            if cell and cell != 'ac':
                actions = cell.split()
                shift_count = sum(1 for action in actions if action.startswith('S'))
                reduce_count = sum(1 for action in actions if action.startswith('R'))

                if shift_count > 0 and reduce_count > 0:
                    sr += 1
                elif reduce_count > 1:
                    rr += 1

    return sr, rr


# Define the numbered rules explicitly for reduction
numbered_rules = {
    1: ("E", ["E", "+", "T"]),
    2: ("E", ["T"]),
    3: ("T", ["T", "*", "F"]),
    4: ("T", ["F"]),
    5: ("F", ["(", "E", ")"]),
    6: ("F", ["id"])
}

import time
import streamlit as st
import graphviz

# Parsing function with incremental updates
def parse_string_with_static_graph(input_tokens, table, rows, cols, start_symbol):
    stack = [0]  # Initial stack with state 0
    input_tokens.append('$')  # Add end-of-input marker

    st.subheader("Parsing Process (Graphical Representation)")
    st.write("The graph will update step-by-step:")

    # Initialize a Graphviz Digraph
    graph = graphviz.Digraph(format="png", engine="dot")
    graph.attr(rankdir="TB", bgcolor="#f0f8ff", fontname="Helvetica")  # Background and font settings

    # Add the Start node
    graph.node("Start", label="Start Parsing", shape="ellipse", style="filled", fillcolor="#87ceeb", fontcolor="black")
    current_node = "Start"

    # Display the graph once at the start
    graph_placeholder = st.graphviz_chart(graph, use_container_width=True)

    step = 1

    while True:
        # Get current state and next input token
        current_state = stack[-1]
        current_token = input_tokens[0]

        # Find the action from the table
        col_index = cols.index(current_token)
        action = table[current_state][col_index].strip()

        # Create a label for the current step
        step_label = f"Step {step}\nStack: {stack}\nInput: {input_tokens}\nAction: {action}"

        # Add the current step to the graph with customized colors
        graph.node(f"Step{step}", label=step_label, shape="box", style="rounded,filled", fillcolor="#dff0d8", fontcolor="black")
        graph.edge(current_node, f"Step{step}", color="#4682b4", penwidth="2.0")  # Blue edges for transitions

        # Update only the newly added node and edge
        current_node = f"Step{step}"
        step += 1

        # Update the graph in Streamlit
        graph_placeholder.graphviz_chart(graph, use_container_width=True)
        time.sleep(1)  # Add a delay to create the animation effect

        if action == "Accept":
            # Add a success node
            graph.node("End", label="Parsing Successful", shape="ellipse", style="filled", fillcolor="#32cd32", fontcolor="white")
            graph.edge(current_node, "End", color="#4682b4", penwidth="2.0")
            # Final update for success
            graph_placeholder.graphviz_chart(graph, use_container_width=True)
            break
        elif action.startswith("S"):  # Shift
            # Extract the state to shift to
            new_state = int(action[1:])
            stack.append(current_token)
            stack.append(new_state)
            input_tokens.pop(0)  # Consume the input token
        elif action.startswith("R"):  # Reduce
            # Extract the production rule index
            rule_index = int(action[1:])
            lhs, rhs = numbered_rules[rule_index]
            # Pop 2 * len(rhs) items from the stack
            for _ in range(2 * len(rhs)):
                stack.pop()
            # Push the LHS non-terminal
            stack.append(lhs)
            # Use the GOTO table to find the next state
            top_state = stack[-2]
            goto_state = int(table[top_state][cols.index(lhs)].strip())
            stack.append(goto_state)
        else:
            # Add an error node
            graph.node("Error", label="Syntax Error", shape="ellipse", style="filled", fillcolor="#ff6347", fontcolor="white")
            graph.edge(current_node, "Error", color="#ff4500", penwidth="2.0")
            # Final update for error
            graph_placeholder.graphviz_chart(graph, use_container_width=True)
            break


# Streamlit App
st.title("SLR(1) Parser Generator")
st.sidebar.header("Grammar Input")
grammar_input = st.sidebar.text_area(
    "Enter Grammar Rules (one per line)",
    value="""E -> E + T | T
T -> T * F | F
F -> ( E ) | id"""
)
nonterm_input = st.sidebar.text_input("Non-Terminals (comma separated)", value="E, T, F")
term_input = st.sidebar.text_input("Terminals (comma separated)", value="id, +, *, (, )")
input_string_raw = st.sidebar.text_input("Input String (space-separated)", value="id * id + id")
generate_btn = st.sidebar.button("Parse String")

if generate_btn:
    # Parse the grammar and input
    rules = [line.strip() for line in grammar_input.splitlines() if line.strip()]
    nonterm_userdef = [x.strip() for x in nonterm_input.split(',')]
    term_userdef = [x.strip() for x in term_input.split(',')]
    start_symbol = nonterm_userdef[0]

    # Generate parsing table (reusing previous code)
    separatedRulesList = grammarAugmentation(rules, nonterm_userdef, start_symbol)
    init_start_symbol = separatedRulesList[0][0]
    I0 = findClosure([separatedRulesList[0]], separatedRulesList[0][1][1], separatedRulesList, init_start_symbol)
    statesDict = {0: I0}
    stateMap = {}
    generateStates(statesDict, stateMap, separatedRulesList)

    diction = {}
    Table, rowStates, cols = createParseTable(
        statesDict,
        stateMap,
        term_userdef,
        nonterm_userdef,
        separatedRulesList,
        rules,
        diction,
        term_userdef,
        separatedRulesList[0][0]
    )

    # Display parsing table
    st.subheader("SLR(1) Parsing Table")
    df = pd.DataFrame(Table, index=[f"I{i}" for i in rowStates], columns=cols)
    st.dataframe(df)

    # Parse the input string with graphical animation
    input_tokens = input_string_raw.split()
    parse_string_with_static_graph(input_tokens, Table, rowStates, cols, start_symbol)
