import os
from pdf2image import convert_from_path
from PIL import Image
import win32com.client
from pathlib import Path
from PyPDF2 import PdfMerger, PdfReader, PdfWriter


folder_path = os.path.dirname(os.path.abspath(__file__))


# Define the specific strings to look for
search_strings = ["DischargeSummery", "ICPs", "OTNotes", "PAC", "OperationDocuments", 
"IntraOPImages", "SpecimenPIC", "PostOPXray", "PostUSG", "PostOPImages", "PostMRI", "PostCT", "AadharCard", "IVP", 
"RationCard", "USG", "PreXray", "CT", "ClinicalPIC", "MedicationChart", "DailyVitals", "IntakeOutput", "TreatmentDetail", "MRI"]


def convert_to_pdf(input_file):
    """Convert various file types to PDF"""
    file_path = Path(input_file)
    output_pdf = str(file_path.with_suffix('.pdf'))
    
    # If file is already PDF, return its path
    if file_path.suffix.lower() == '.pdf':
        return input_file
        
        
    # Convert images to PDF
    if file_path.suffix.lower() in ['.png', '.jpg', '.jpeg']:
        image = Image.open(input_file)
        rgb_image = image.convert('RGB')
        rgb_image.save(output_pdf)
        return output_pdf
        
    return None

try:
    # List all files in the directory
    files = os.listdir(folder_path)
    
    # Create a dictionary to store files by category
    categorized_files = {category: [] for category in search_strings}
    other_files = []
    
    # Categorize files based on the search strings
    for file in files:
        categorized = False
        for category in search_strings:
            if category.lower() in file.lower():
                categorized_files[category].append(os.path.join(folder_path, file))
                categorized = True
                break
        if not categorized:
            other_files.append(file)
    
    # Process each category
    for category, file_list in categorized_files.items():
        if file_list:  # Only process categories that have files
            print(f"\nProcessing {category} files:")
            pdf_files = []
            
            # Convert each file to PDF
            for file_path in file_list:
                print(f"  Converting: {os.path.basename(file_path)}")
                pdf_path = convert_to_pdf(file_path)
                if pdf_path:
                    pdf_files.append(pdf_path)
            
            # Merge PDFs if there are any
            if pdf_files:
                merger = PdfMerger()
                for pdf in pdf_files:
                    merger.append(pdf)
                
                # Save the merged PDF with category name
                output_path = os.path.join(folder_path, f"{category}.pdf")
                merger.write(output_path)
                merger.close()
                
                print(f"  Created combined PDF: {category}.pdf")
                
                # Clean up temporary PDF files
                for pdf in pdf_files:
                    if pdf != output_path and os.path.basename(pdf) != os.path.basename(output_path):
                        try:
                            os.remove(pdf)
                        except:
                            pass
# ... existing code remains the same until after the category processing loop ...

    # Process each category
    for category, file_list in categorized_files.items():
        if file_list:  # Only process categories that have files
            print(f"\nProcessing {category} files:")
            pdf_files = []
            
            # Convert each file to PDF
            for file_path in file_list:
                print(f"  Converting: {os.path.basename(file_path)}")
                pdf_path = convert_to_pdf(file_path)
                if pdf_path:
                    pdf_files.append(pdf_path)
            
            # Merge PDFs if there are any
            if pdf_files:
                merger = PdfMerger()
                for pdf in pdf_files:
                    merger.append(pdf)
                
                # Save the merged PDF with category name
                output_path = os.path.join(folder_path, f"{category}.pdf")
                merger.write(output_path)
                merger.close()
                
                print(f"  Created combined PDF: {category}.pdf")
                
                # Clean up temporary PDF files
                for pdf in pdf_files:
                    if pdf != output_path and os.path.basename(pdf) != os.path.basename(output_path):
                        try:
                            os.remove(pdf)
                        except:
                            pass
    
    # Create OperationDocument by combining OTNotes and PAC
    if os.path.exists(os.path.join(folder_path, "OTNotes.pdf")) and os.path.exists(os.path.join(folder_path, "PAC.pdf")):
        merger = PdfMerger()
        merger.append(os.path.join(folder_path, "OTNotes.pdf"))
        merger.append(os.path.join(folder_path, "PAC.pdf"))
        output_path = os.path.join(folder_path, "OperationDocument.pdf")
        merger.write(output_path)
        merger.close()
        print("\nCreated OperationDocument.pdf by combining OTNotes and PAC")


except FileNotFoundError:
    print("Folder not found!")
except PermissionError:
    print("Permission denied to access the folder!")
except Exception as e:
    print(f"An error occurred: {str(e)}")