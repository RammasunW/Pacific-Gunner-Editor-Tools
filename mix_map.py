import tkinter as tk
from tkinter import filedialog

# Create a root window
root = tk.Tk()
root.withdraw()

# Show the file dialog box and get the first file path
file_path_1 = filedialog.askopenfilename(title="Select first map file")
print(f"Selected file 1: {file_path_1}")

# Show the file dialog box and get the second file path
file_path_2 = filedialog.askopenfilename(title="Select second map file")
print(f"Selected file 2: {file_path_2}")

# Show the file dialog box and get the output file path
output_file_path = filedialog.asksaveasfilename(title="Save output file as", defaultextension=".map")
print(f"Output file: {output_file_path}")

# Open the first file and read its contents, ignore the final lines "end:\n"
with open(file_path_1, 'r') as f:
    contents_1 = f.readlines()[:-1]

# Open the second file and read its contents, ignore the final lines "end:\n"
with open(file_path_2, 'r') as f:
    contents_2 = f.readlines()[:-1]

# Process the contents of both files and write the output to the output file
with open(output_file_path, 'w') as f:
    for line_1, line_2 in zip(contents_1, contents_2):
        numbers_1 = [int(num) for num in line_1.strip().split()]
        numbers_2 = [int(num) for num in line_2.strip().split()]
        highest_numbers = [str(max(num_1, num_2)) for num_1, num_2 in zip(numbers_1, numbers_2)]
        output_line = ' '.join(highest_numbers) + ' \n'
        f.write(output_line)

    # Add the 'end:' and empty line back to the output file
    f.write("end:\n")

