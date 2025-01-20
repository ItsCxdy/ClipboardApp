import os
from PIL import Image
import win32com.client
from pathlib import Path
from PyPDF2 import PdfMerger, PdfReader, PdfWriter

# Add these new imports at the top
from PIL import Image
import io

folder_path = os.path.dirname(os.path.abspath(__file__))

# Define the specific strings to look for
search_strings = ["DischargeSummery", "ICPs", "OTNotes", "PAC", "OperationDocuments", 
"IntraOPImages", "SpecimenPIC", "PostOPXray", "PostUSG", "PostOPImages", "PostMRI", "PostCT", "AadharCard", "IVP", 
"RationCard", "USG", "PreXray", "CT", "ClinicalPIC", "MedicationChart", "DailyVitals", "IntakeOutput", "TreatmentDetail", "MRI"]

def convert_to_pdf(input_file, compress=False):
    """Convert various file types to PDF with optional compression"""
    file_path = Path(input_file)
    output_pdf = str(file_path.with_suffix('.pdf'))
    
    # If file is already PDF, return its path
    if file_path.suffix.lower() == '.pdf':
        return input_file
        
    # Convert and compress images to PDF
    if file_path.suffix.lower() in ['.png', '.jpg', '.jpeg']:
        image = Image.open(input_file)
        if compress:
            # Convert to RGB and apply compression
            rgb_image = image.convert('RGB')
            
            # Resize image if it's too large (reduced max dimension)
            max_size = 1000  # Reduced from 1500
            if max(rgb_image.size) > max_size:
                ratio = max_size / max(rgb_image.size)
                new_size = tuple(int(dim * ratio) for dim in rgb_image.size)
                rgb_image = rgb_image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Create a BytesIO object to check size
            temp_buffer = io.BytesIO()
            quality = 85  # Start with lower quality
            while quality >= 15:  # Even lower minimum quality
                temp_buffer.seek(0)
                temp_buffer.truncate()
                
                # Try to reduce size further if quality is low
                if quality < 30:
                    # Additional size reduction for very low quality
                    curr_size = rgb_image.size
                    reduced_size = tuple(int(dim * 0.8) for dim in curr_size)
                    temp_img = rgb_image.resize(reduced_size, Image.Resampling.LANCZOS)
                else:
                    temp_img = rgb_image
                
                temp_img.save(temp_buffer, 'JPEG', 
                            quality=quality, 
                            optimize=True,
                            dpi=(96, 96))  # Lower DPI further
                
                if len(temp_buffer.getvalue()) <= 499 * 1024:  # 499 KB
                    break
                quality -= 10  # Larger quality reduction steps
            
            # Save the compressed image as PDF
            rgb_image = Image.open(temp_buffer)
        else:
            rgb_image = image.convert('RGB')
            
        # Save with maximum compression settings
        rgb_image.save(output_pdf, 'PDF', 
                      resolution=96,  # Even lower resolution
                      optimize=True)
        return output_pdf
        
    return None

def compress_pdf(input_path, max_size_kb=499):
    """Compress PDF file to meet the size requirement"""
    if os.path.getsize(input_path) <= max_size_kb * 1024:
        return
        
    print(f"Compressing {os.path.basename(input_path)}...")
    
    try:
        # First try: Convert PDF to images and back with compression
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        for page in reader.pages:
            # Convert page to image with low DPI
            img = Image.new('RGB', (800, 1000), 'white')  # Smaller fixed size
            # Add the page as image
            writer.add_page(page)
        
        # Try increasingly aggressive compression
        for quality in [70, 50, 30, 15]:  # More aggressive quality reduction
            output_bytes = io.BytesIO()
            writer.write(output_bytes)
            
            if len(output_bytes.getvalue()) <= max_size_kb * 1024:
                with open(input_path, 'wb') as f:
                    f.write(output_bytes.getvalue())
                print(f"Successfully compressed to {os.path.getsize(input_path) // 1024} KB")
                return
            
            # Apply more aggressive compression
            for page in writer.pages:
                page.compress_content_streams()
                # Remove unnecessary elements
                if hasattr(page, '/Resources'):
                    page['/Resources'] = {}
                if hasattr(page, '/Annots'):
                    del page['/Annots']
        
        print("Warning: Could not compress to target size while maintaining acceptable quality")
            
    except Exception as e:
        print(f"Error during compression: {str(e)}")

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
            
            # Convert each file to PDF with compression
            for file_path in file_list:
                print(f"  Converting: {os.path.basename(file_path)}")
                pdf_path = convert_to_pdf(file_path, compress=True)  # Enable compression during conversion
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
                # Add compression check
                compress_pdf(output_path)
                
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
        # Add compression check
        compress_pdf(output_path)

        


except FileNotFoundError:
    print("Folder not found!")
except PermissionError:
    print("Permission denied to access the folder!")
except Exception as e:
    print(f"An error occurred: {str(e)}")