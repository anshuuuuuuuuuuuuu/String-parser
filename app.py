import streamlit as st
import time
import graphviz

def parse_grammar(grammar_input):
    grammar_rules = {}
    for line in grammar_input.strip().split("\n"):
        parts = line.split(":")
        if len(parts) == 2:
            rule_num = int(parts[0].strip())
            lhs, rhs = parts[1].split("->")
            lhs = lhs.strip()
            rhs = rhs.strip().split()
            rhs = ['#'] if rhs == ["ε"] else rhs  
            grammar_rules[rule_num] = (lhs, rhs)
    return grammar_rules

def parse_string(input_tokens, parsing_table, row_states, cols, grammar_rules):
    stack = [0]
    input_tokens.append('$')
    st.subheader("Parsing Process (Graphical Representation)")
    st.write("The graph will update step-by-step:")
    graph = graphviz.Digraph(format="png", engine="dot")
    graph.attr(rankdir="TB", bgcolor="#f0f8ff", fontname="Helvetica")
    graph.node("Start", label="Start Parsing", shape="ellipse", style="filled", fillcolor="#87ceeb")
    current_node = "Start"
    graph_placeholder = st.graphviz_chart(graph, use_container_width=True)
    step = 1

    while True:
        current_state = stack[-1]
        current_token = input_tokens[0]

        if current_token not in cols:
            graph.node("Error", label=f"Invalid Token: '{current_token}'", shape="ellipse", style="filled", fillcolor="#ff6347")
            graph.edge(current_node, "Error", color="#ff4500", penwidth="2.0")
            graph_placeholder.graphviz_chart(graph, use_container_width=True)
            st.error(f"❌ Invalid token found: '{current_token}' → **String is invalid**")
            return

        col_index = cols.index(current_token)
        action = parsing_table[current_state][col_index]

        if action is None:
            graph.node("Error", label=f"Syntax Error at '{current_token}'", shape="ellipse", style="filled", fillcolor="#ff6347")
            graph.edge(current_node, "Error", color="#ff4500", penwidth="2.0")
            graph_placeholder.graphviz_chart(graph, use_container_width=True)
            st.error(f"❌ No valid action found for '{current_token}' in state {current_state} → **String is invalid**")
            return

        step_label = f"Step {step}\nStack: {stack}\nInput: {input_tokens}\nAction: {action}"
        graph.node(f"Step{step}", label=step_label, shape="box", style="rounded,filled", fillcolor="#dff0d8")
        graph.edge(current_node, f"Step{step}", color="#4682b4", penwidth="2.0")
        current_node = f"Step{step}"
        step += 1
        graph_placeholder.graphviz_chart(graph, use_container_width=True)
        time.sleep(1)

        if action == "Accept":
            graph.node("End", label="Parsing Successful", shape="ellipse", style="filled", fillcolor="#32cd32")
            graph.edge(current_node, "End", color="#4682b4", penwidth="2.0")
            graph_placeholder.graphviz_chart(graph, use_container_width=True)
            st.success("✅ The input string is **valid** according to the given SLR(1) parsing table.")
            break
        elif action.startswith("S"):
            new_state = int(action[1:])
            stack.append(current_token)
            stack.append(new_state)
            input_tokens.pop(0)
        elif action.startswith("R"):
            rule_index = int(action[1:])
            if rule_index not in grammar_rules:
                st.error(f"❌ Reduction rule {rule_index} not found → String is **invalid**")
                return

            lhs, rhs = grammar_rules[rule_index]
            for _ in range(2 * len(rhs)):  
                stack.pop()

            stack.append(lhs)
            top_state = stack[-2]
            if lhs in cols:
                goto_index = cols.index(lhs)
                goto_action = parsing_table[top_state][goto_index]
                if goto_action and goto_action.isdigit():
                    goto_state = int(goto_action)
                    stack.append(goto_state)
                else:
                    st.error("❌ GOTO state not found → String is **invalid**")
                    return
        else:
            graph.node("Syntax Error", label="Syntax Error", shape="ellipse", style="filled", fillcolor="#ff6347")
            graph.edge(current_node, "Syntax Error", color="#ff4500", penwidth="2.0")
            graph_placeholder.graphviz_chart(graph, use_container_width=True)
            st.error("❌ The input string is **not valid** according to the given SLR(1) parsing table.")
            break

st.title("SLR(1) Parser with Step-by-Step Visualization")

st.sidebar.header("Parsing Table Input")

cols_input = st.sidebar.text_area("Enter Parsing Table Columns (Space-separated):", "id + * ( ) $ E T F")
table_input = st.sidebar.text_area("Enter Parsing Table (Rows separated by newlines, Columns by spaces):", 
"""I0  S5  -  -  S4  -  -  1  2  3
I1  -  S6  -  -  -  Accept  -  -  -
I2  -  R2  S7  -  R2  R2  -  -  -
I3  -  R4  R4  -  R4  R4  -  -  -
I4  S5  -  -  S4  -  -  8  2  3
I5  -  R6  R6  -  R6  R6  -  -  -
I6  S5  -  -  S4  -  -  -  9  3
I7  S5  -  -  S4  -  -  -  -  10
I8  -  S6  -  -  S11  -  -  -  -
I9  -  R1  S7  -  R1  R1  -  -  -
I10 -  R3  R3  -  R3  R3  -  -  -
I11 -  R5  R5  -  R5  R5  -  -  -
""")

st.sidebar.header("Grammar Rules (Epsilon replaced with #)")
grammar_input = st.sidebar.text_area("Enter Grammar Rules (Numbered):", 
"""1: E -> E + T
2: E -> T
3: T -> T * F
4: T -> F
5: F -> ( E )
6: F -> id
""")

st.sidebar.header("Input String")
input_string = st.sidebar.text_input("Enter input string (space-separated):", "id * id + id")

parse_button = st.sidebar.button("Parse String")

if parse_button:
    table_lines = table_input.strip().split("\n")
    cols = cols_input.strip().split()
    
    row_states = []
    parsing_table = []
    
    for line in table_lines:
        parts = line.split()
        state = int(parts[0][1:])
        row_states.append(state)
        
        row = [None if part == "-" else part for part in parts[1:]]
        parsing_table.append(row)

    grammar_rules = parse_grammar(grammar_input)

    input_tokens = input_string.split()

    parse_string(input_tokens, parsing_table, row_states, cols, grammar_rules)
