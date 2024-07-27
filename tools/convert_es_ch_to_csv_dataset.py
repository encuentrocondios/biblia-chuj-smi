import xmltodict
import pandas as pd
import os
import xml.parsers.expat

# Input file paths
input_xml_file_chuj = 'CHSM.xml'
input_xml_file_spanish = 'SPARV.xml'
output_csv_file = 'output/verses.csv'

def parse_xml(file_path):
    with open(file_path, 'r', encoding='utf-8') as xml_file:
        try:
            data = xmltodict.parse(xml_file.read())
            print(f"XML from {file_path} parsed successfully.")
            return data
        except xml.parsers.expat.ExpatError as e:
            print(f"ExpatError while parsing {file_path}: {e}")
            parse_xml_line_by_line(file_path)
            exit()
        except Exception as e:
            print(f"An error occurred while parsing {file_path}: {e}")
            exit()

def parse_xml_line_by_line(file_path):
    with open(file_path, 'r', encoding='utf-8') as xml_file:
        lines = xml_file.readlines()

    for i, line in enumerate(lines, start=1):
        try:
            xmltodict.parse(line)
        except xml.parsers.expat.ExpatError as e:
            print(f"ExpatError at line {i}: {e}")
            break

def extract_verses(data, lang):
    verses = {}
    for book_data in data['XMLBIBLE']['BIBLEBOOK']:
        book_name = book_data['@bname'].lower()  # Use lowercase for consistent comparison
        book_number = book_data['@bnumber']  # Use the book number for sorting
        if isinstance(book_data['CHAPTER'], list):
            chapters = book_data['CHAPTER']
        else:
            chapters = [book_data['CHAPTER']]
        
        for chapter_data in chapters:
            chapter_number = chapter_data['@cnumber']
            for verse_data in chapter_data['VERS']:
                verse_number = verse_data['@vnumber']
                verse_text = verse_data['#text']
                if lang == 'chuj':
                    verses[(int(book_number), int(chapter_number), int(verse_number))] = (book_name, verse_text)
                else:
                    verses[(int(book_number), int(chapter_number), int(verse_number))] = (book_name, verse_text)
    return verses

# Parse both XML files
data_chuj = parse_xml(input_xml_file_chuj)
data_spanish = parse_xml(input_xml_file_spanish)

# Extract verses from both XML files into dictionaries
verses_chuj = extract_verses(data_chuj, 'chuj')
verses_spanish = extract_verses(data_spanish, 'spanish')

# Create DataFrames for Chuj and Spanish verses
rows_chuj = []
for key, (book_name, verse_text) in verses_chuj.items():
    book_number, chapter_number, verse_number = key
    rows_chuj.append([book_number, book_name, chapter_number, verse_number, verse_text])

df_chuj = pd.DataFrame(rows_chuj, columns=['BookNumber', 'Book', 'Chapter', 'Verse', 'Chuj'])

rows_spanish = []
for key, (book_name, verse_text) in verses_spanish.items():
    book_number, chapter_number, verse_number = key
    rows_spanish.append([book_number, book_name, chapter_number, verse_number, verse_text])

df_spanish = pd.DataFrame(rows_spanish, columns=['BookNumber', 'Book', 'Chapter', 'Verse', 'Spanish'])

# Merge the DataFrames on BookNumber, Chapter, and Verse
df_combined = pd.merge(df_chuj, df_spanish, on=['BookNumber', 'Book', 'Chapter', 'Verse'], how='outer')

# Sort the combined DataFrame
df_combined.sort_values(by=['BookNumber', 'Chapter', 'Verse'], inplace=True)

# Drop the BookNumber column
df_combined.drop(columns=['BookNumber'], inplace=True)

# Write the combined DataFrame to a CSV file
os.makedirs('output', exist_ok=True)
df_combined.to_csv(output_csv_file, index=False, encoding='utf-8', quotechar='"')

print(f"CSV file created successfully: {output_csv_file}")
