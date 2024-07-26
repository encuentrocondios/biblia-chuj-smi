import xmltodict
import json
import os
import xml.parsers.expat

# Input and output file paths
input_xml_file = 'CHSM.xml'
output_dir = 'output'

def parse_xml_line_by_line(file_path):
    with open(file_path, 'r', encoding='utf-8') as xml_file:
        lines = xml_file.readlines()

    for i in range(len(lines)):
        try:
            xmltodict.parse(''.join(lines[:i+1]))
        except xml.parsers.expat.ExpatError as e:
            print(f"ExpatError at line {i+1}: {e}")
            break



# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Load the Zefania XML data
# with open(input_xml_file, 'r', encoding='utf-8') as xml_file:
#     data = xmltodict.parse(xml_file.read())
    
try:
    with open(input_xml_file, 'r', encoding='utf-8') as xml_file:
        data = xmltodict.parse(xml_file.read())
    print("XML parsed successfully.")
except xml.parsers.expat.ExpatError as e:
    print(f"ExpatError while parsing entire file: {e}")
    parse_xml_line_by_line(input_xml_file)
except Exception as e:
    print(f"An error occurred: {e}")

# Create a JSON file containing the list of books
books = [{'name': book['@bname'], 'short_name': book['@bsname']} for book in data['XMLBIBLE']['BIBLEBOOK']]
with open(os.path.join(output_dir, 'books.json'), 'w', encoding='utf-8') as books_json_file:
    json.dump(books, books_json_file, ensure_ascii=False, indent=4)

# Create JSON files for chapters and verses
for book_data in data['XMLBIBLE']['BIBLEBOOK']:
    book_name = book_data['@bname']
    book_short_name = book_data['@bsname']
    book_output_dir = os.path.join(output_dir, book_short_name)
    print(f"{book_name}=> {book_output_dir}")

    # Create a directory for each book
    os.makedirs(book_output_dir, exist_ok=True)

    # Check if CHAPTER is a list or a dictionary
    if isinstance(book_data['CHAPTER'], list):
        chapters = book_data['CHAPTER']
    else:
        chapters = [book_data['CHAPTER']]

    for chapter_data in chapters:
        chapter_number = chapter_data['@cnumber']
        chapter_output_file = os.path.join(book_output_dir, f'{chapter_number}.json')

        # Extract verses
        verses = [{'number': verse['@vnumber'], 'text': verse['#text']} for verse in chapter_data['VERS']]

        # Create a dictionary containing chapter and verses
        chapter_and_verses = {
            'chapter': chapter_number,
            'verses': verses
        }

        # Write the chapter and verses to a JSON file
        with open(chapter_output_file, 'w', encoding='utf-8') as chapter_json_file:
            json.dump(chapter_and_verses, chapter_json_file, ensure_ascii=False, indent=4)
