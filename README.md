### Demo Link
https://slr-string-parser.streamlit.app/

# SLR(1) Parser with Step-by-Step Visualization

This project implements an **SLR(1) Parser** using **Streamlit** for interactive visualization and **Graphviz** for graphical representation of the parsing process. The parser processes an input string based on a user-defined **parsing table** and **grammar rules**, providing step-by-step feedback and error handling.

## Features
- **Interactive Streamlit Interface** for inputting grammar rules, parsing tables, and input strings.
- **Graphical Parsing Visualization** using Graphviz.
- **Error Handling and Debugging Assistance** with color-coded error messages.
- **Step-by-step Parsing Process** to track stack changes, input consumption, and parsing decisions.

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/anshuuuuuuuuuuuuu/String-parser.git
   cd String-parser
   ```

2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

3. Run the Streamlit application:
   ```sh
   streamlit run app.py
   ```

## Usage

1. **Enter Parsing Table Columns** (terminals and non-terminals).
2. **Define Parsing Table Rows** (state transitions and actions).
3. **Specify Grammar Rules** in a numbered format.
4. **Provide an Input String** for parsing.
5. Click the **Parse String** button to visualize the parsing process step-by-step.

## Example

### Input:
#### Parsing Table Columns:
```
id + * ( ) $ E T F
```

#### Parsing Table:
```
I0  S5  -  -  S4  -  -  1  2  3
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
```

#### Grammar Rules:
```
1: E -> E + T
2: E -> T
3: T -> T * F
4: T -> F
5: F -> ( E )
6: F -> id
```

#### Input String:
```
id * id + id
```

### Output:
- Step-by-step parsing visualization with Graphviz.
- Success or failure message based on parsing result.
- Debugging information in case of errors.

## Technologies Used
- **Python**
- **Streamlit**
- **Graphviz**


