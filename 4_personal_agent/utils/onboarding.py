import csv
import os

class Onboarding():

    def __init__(self, path="./assets/onboarding.csv"):
        self.path = path

    def read(self):
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"File not found: {self.path}")

        formatted_rows = []

        with open(self.path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                # Skip empty rows
                if not any(cell.strip() for cell in row):
                    continue

                # Replace empty cells with "-" and keep the cols quantity
                row_str = ",".join(cell.strip() if cell.strip() != "" else "-" for cell in row)
                formatted_rows.append(row_str)

        return "\n".join(formatted_rows)

    def read_as_markdown(self) -> str:
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"File not found: {self.path}")

        rows = []

        with open(self.path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if not any(cell.strip() for cell in row):
                    continue
                # Replace empty cells with "-"
                clean_row = [cell.strip() if cell.strip() != "" else "-" for cell in row]
                rows.append(clean_row)

        # Generate markdown table
        # If the file is empty or has no valid rows, return a message
        if not rows:
            return "Empty table or no valid rows found."

        header = rows[0]
        body = rows[1:]

        markdown = []

        # Header
        markdown.append("| " + " | ".join(header) + " |")
        markdown.append("|" + "|".join("-" * (len(h) + 2) for h in header) + "|")

        # Body
        for row in body:
            markdown.append("| " + " | ".join(row) + " |")

        return "\n".join(markdown)

if __name__ == "__main__":

    obj = Onboarding()

    # text = obj.read() # Read as plain text
    text = obj.read_as_markdown() # Read as markdown

    print(text)
