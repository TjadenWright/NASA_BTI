def filter_and_replace_log_lines(input_file, output_file, phrase_replacements):
    # Open the input file for reading
    with open(input_file, 'r') as infile:
        # Open the output file for writing
        with open(output_file, 'w') as outfile:
            # Iterate through each line in the input file
            for line in infile:
                # Check if any of the specified phrases are in the current line
                for phrase, replacement in phrase_replacements.items():
                    if phrase in line:
                        # Replace the phrase with the corresponding replacement
                        line = line.replace(phrase, replacement)
                        # Write the modified line to the output file
                        outfile.write(line)
                        # Break to avoid writing the same line multiple times if multiple phrases match
                        break

if __name__ == "__main__":
    # Define the input and output file names
    input_file = "arduino_log.txt"
    output_file = "leonardo_log_done.txt"
    
    # Define the dictionary of phrases to replacements
    phrase_replacements = {
        "cMotor 2": "Pivot",
        "cMotor 4": "Front Auger",
        "cMotor 5": "Bucketwheel",
        "cMotor 13": "Arm Lift"
    }
    
    # Call the function to filter and replace the log lines
    filter_and_replace_log_lines(input_file, output_file, phrase_replacements)

