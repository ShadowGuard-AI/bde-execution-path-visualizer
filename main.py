import argparse
import logging
import os
import subprocess
import re
import tempfile
import shutil

try:
    import jsbeautifier
except ImportError:
    print("Error: Missing dependencies. Please install jsbeautifier.")
    exit(1)


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Core Functions ---

def setup_argparse():
    """Sets up the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        description="bde-Execution-Path-Visualizer: Writes a dot file with a flat list of call shaped names found in a script. No branching or control flow structure is represented."
    )
    parser.add_argument("input_file", help="The input script file (JavaScript, PowerShell, etc.)")
    parser.add_argument(
        "-o",
        "--output_file",
        default="execution_path.dot",
        help="The output file for the Graphviz dot representation (default: execution_path.dot)",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )
    parser.add_argument(
        "--beautify", action="store_true", help="Beautify the input script before analysis."
    )
    parser.add_argument(
        "--decode_strings", action="store_true", help="Attempt to decode encoded strings: base64 in the Python b'...' literal shape, and hex only inside a quoted 0x literal such as '0x41'. Numeric literals such as 0x10 outside quotes are left alone."
    )
    parser.add_argument(
        "--rename_variables", action="store_true", help="Attempt to rename obfuscated variables."
    )

    return parser.parse_args()


def beautify_code(input_code):
    """Beautifies the input code using jsbeautifier."""
    try:
        opts = jsbeautifier.default_options()
        opts.indent_size = 4
        return jsbeautifier.beautify(input_code, opts)
    except Exception as e:
        logging.error(f"Error beautifying code: {e}")
        return input_code


def decode_strings(input_code):
    """Decodes base64 and hex encoded strings within the code.

    Base64 matching covers the Python b'...' literal shape only. Hex
    matching covers a quoted 0x literal only; numeric literals outside
    quotes are left unchanged.
    """
    try:
        # Decode base64 strings
        base64_pattern = re.compile(r"b\'([A-Za-z0-9+/=]+)\'")
        matches = base64_pattern.findall(input_code)
        for match in matches:
            try:
                import base64
                decoded_string = base64.b64decode(match).decode('utf-8', errors='ignore')
                input_code = input_code.replace(f"b\'{match}\'", f"'{decoded_string}'")
            except Exception as e:
                logging.warning(f"Failed to decode base64 string: {match} - {e}")

        # Decode hex encoded strings, but only inside quotes. A bare
        # 0x10 in code is a numeric literal, not a string: rewriting it
        # as a character changed what the code means (0x10 became a raw
        # control character). A quoted literal such as '0x41' or
        # "0x48656c6c6f" is a string, so its hex digits decode as bytes.
        def _decode_quoted_hex(m):
            quote, digits = m.group(1), m.group(2)
            if len(digits) % 2:
                digits = "0" + digits
            try:
                decoded = bytes.fromhex(digits).decode('utf-8', errors='ignore')
            except Exception as e:
                logging.warning(f"Failed to decode hex string: {m.group(0)} - {e}")
                return m.group(0)
            return f"{quote}{decoded}{quote}"

        hex_pattern = re.compile(r"(['\"])0x([0-9a-fA-F]+)\1")
        input_code = hex_pattern.sub(_decode_quoted_hex, input_code)
        return input_code
    except Exception as e:
        logging.error(f"Error decoding strings: {e}")
        return input_code


def rename_variables(input_code):
     """Renames obfuscated variables to improve readability."""
     # This is a simplified example. A fuller implementation would require
     # parsing the code and understanding variable scope.
     try:
        variable_pattern = re.compile(r"\b(_\w+)\b") # match underscore starting variables
        matches = variable_pattern.findall(input_code)
        renamed_vars = {}
        counter = 1
        for match in matches:
            if match not in renamed_vars:
                renamed_vars[match] = f"var_{counter}"
                counter += 1

        for old_name, new_name in renamed_vars.items():
            # Word boundaries, not a plain replace: replacing the string
            # _a would also rewrite the head of _abc and split that
            # variable into a name nothing else uses.
            input_code = re.sub(rf"\b{re.escape(old_name)}\b", new_name, input_code)
        return input_code
     except Exception as e:
         logging.error(f"Error renaming variables: {e}")
         return input_code



def generate_call_graph(input_file, code=None):
    """Generates a call graph representation using a simplified approach (for demonstration)."""
    try:
        if code is None:
            with open(input_file, "r") as f:
                code = f.read()

        # Basic function call detection (very naive)
        function_calls = re.findall(r"(\w+)\s*\(", code) # Match function calls like functionName(

        dot_code = "digraph ExecutionPath {\n"
        dot_code += "  rankdir=LR;\n"  # Left-to-right layout
        dot_code += "  node [shape=box];\n" # Make nodes boxes

        # Represent the main script as the entry point
        dot_code += f'  "MainScript" [label="{input_file}", shape=ellipse];\n'

        for call in function_calls:
            dot_code += f'  "MainScript" -> "{call}";\n'  # Main script calls the function
            dot_code += f'  "{call}" [label="{call}"];\n' #Function name as label

        dot_code += "}\n"
        return dot_code

    except FileNotFoundError:
        logging.error(f"Error: Input file not found: {input_file}")
        return None
    except Exception as e:
        logging.error(f"Error generating call graph: {e}")
        return None


def main():
    """Main function to orchestrate the process."""
    args = setup_argparse()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logging.debug("Starting bde-Execution-Path-Visualizer...")

    # Input validation
    if not os.path.isfile(args.input_file):
        logging.error(f"Error: Input file does not exist: {args.input_file}")
        raise SystemExit(1)

    try:
        # Read the input file
        with open(args.input_file, "r") as f:
            code = f.read()

        # Optional code transformations
        if args.beautify:
            code = beautify_code(code)
        if args.decode_strings:
            code = decode_strings(code)
        if args.rename_variables:
            code = rename_variables(code)


        # The transformed text is what gets graphed. This call used to
        # re-read the file from disk, so --beautify, --decode_strings and
        # --rename_variables computed new code and then threw it away.
        dot_code = generate_call_graph(args.input_file, code)

        if dot_code:
            # Write the dot code to the output file
            with open(args.output_file, "w") as f:
                f.write(dot_code)

            logging.info(f"Call graph written to: {args.output_file}")
            print(f"Call graph written to: {args.output_file}") #For demonstration
        else:
            logging.error("Failed to generate call graph.")
            raise SystemExit(1)

    except SystemExit:
        raise
    except Exception as e:
        logging.exception(f"An unexpected error occurred: {e}")
        raise SystemExit(1)


# --- Usage Example ---
if __name__ == "__main__":
    # Example usage (for demonstration):
    # 1. Create a dummy JavaScript file:
    #    echo 'function myFunction() { console.log("Hello"); } myFunction();' > test.js
    # 2. Run the script:
    #    python main.py test.js -o graph.dot --beautify --decode_strings --rename_variables

    main()