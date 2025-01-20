import tkinter as tk
from tkinter import messagebox
import os
from tkinter import ttk

# File to store the text
DATA_FILE = "clipboard_data.txt"

def load_data():
    """Load text data from file."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return [line.strip() for line in file.readlines()]
    return []

def save_data(data):
    """Save text data to file."""
    with open(DATA_FILE, "w") as file:
        file.writelines(f"{line}\n" for line in data)

def add_text():
    """Add text from input box to the list."""
    text = input_box.get("1.0", tk.END).strip()
    if not text:
        messagebox.showwarning("Input Error", "Please enter some text!")
        return

    # Add to the list and update the display
    items.append(text)
    save_data(items)
    refresh_list()
    input_box.delete("1.0", tk.END)

def search_items(event=None):
    """Search and sort items based on search text."""
    search_text = search_var.get().lower()
    
    # Sort items based on similarity to search text
    sorted_items = []
    sorted_indices = []  # Keep track of original indices
    
    if search_text:
        # Add items that start with search text first
        for i, item in enumerate(items):
            if item.lower().startswith(search_text):
                sorted_items.append(item)
                sorted_indices.append(i)
                
        # Then add items that contain search text
        for i, item in enumerate(items):
            if search_text in item.lower() and not item.lower().startswith(search_text):
                sorted_items.append(item)
                sorted_indices.append(i)
                
        # Finally add remaining items
        for i, item in enumerate(items):
            if i not in sorted_indices:
                sorted_items.append(item)
                sorted_indices.append(i)
    else:
        sorted_items = items.copy()
        sorted_indices = list(range(len(items)))
    
    # Refresh display with sorted items and their indices
    refresh_list(sorted_items, sorted_indices)

def refresh_list(display_items=None, display_indices=None):
    """Refresh the listbox with updated items."""
    if display_items is None:
        display_items = items
        display_indices = list(range(len(items)))
        
    for widget in items_frame.winfo_children():
        widget.destroy()
    
    check_vars.clear()
    
    for i, (item, orig_index) in enumerate(zip(display_items, display_indices)):
        var = tk.BooleanVar()
        # Set checkbox state based on whether item is in selected_items
        if item in selected_items:
            var.set(True)
        checkbox = tk.Checkbutton(items_frame, text=item, variable=var, 
                                command=lambda idx=orig_index, v=var: toggle_item(idx, v))
        checkbox.pack(anchor="w")
        check_vars.append(var)

def toggle_item(index, var):
    """Update the selected text display when a checkbox is toggled."""
    if var.get():
        selected_items.add((items[index], len(selected_items) + 1))
    else:
        # Remove the item and reindex remaining items
        selected_items.discard(next(item for item in selected_items if item[0] == items[index]))
        # Reindex remaining items
        selected_items_list = sorted(selected_items, key=lambda x: x[1])
        selected_items.clear()
        selected_items.update((item[0], i+1) for i, item in enumerate(selected_items_list))
    update_selected_panel()

def update_selected_panel():
    """Update the panel displaying selected text."""
    # Sort items by their selection order
    sorted_items = sorted(selected_items, key=lambda x: x[1])
    
    # Add serial numbers to selected items based on selection order
    numbered_items = [f"{item[1]}. {item[0]}" for item in sorted_items]
    
    # Add the hardcoded message at the end
    message = "\nWe can submit any document or image in the next query, if required. Please consider this."
    
    # Join all items with numbers and add message
    selected_text = "\n".join(numbered_items) + message
    
    selected_panel.config(state="normal")
    selected_panel.delete("1.0", tk.END)
    selected_panel.insert("1.0", selected_text)
    selected_panel.config(state="disabled")

def clear_checkboxes():
    """Clear all selected checkboxes."""
    for var in check_vars:
        var.set(False)
    selected_items.clear()
    update_selected_panel()

def copy_selected_text():
    """Copy selected text to clipboard."""
    selected_panel.config(state="normal")
    text = selected_panel.get("1.0", tk.END)
    root.clipboard_clear()
    root.clipboard_append(text)
    selected_panel.config(state="disabled")
    messagebox.showinfo("Success", "Text copied to clipboard!")

def on_double_click(event):
    """Handle double click on a list item."""
    # Get the clicked widget
    widget = event.widget
    
    # Get the text of the clicked item
    if isinstance(widget, tk.Checkbutton):
        item_text = widget.cget("text")
        index = items.index(item_text)
        
        # Create popup dialog
        popup = tk.Toplevel(root)
        popup.title("Edit/Delete Item")
        popup.geometry("400x250")
        popup.transient(root)
        
        # Add text widget
        edit_text = tk.Text(popup, height=5, width=40)
        edit_text.pack(padx=10, pady=10)
        edit_text.insert("1.0", item_text)
        
        def save_changes():
            new_text = edit_text.get("1.0", "end-1c")
            if new_text.strip():
                items[index] = new_text
                # Update selected items if the edited item was selected
                if item_text in [item[0] for item in selected_items]:
                    order = next(item[1] for item in selected_items if item[0] == item_text)
                    selected_items.discard(next(item for item in selected_items if item[0] == item_text))
                    selected_items.add((new_text, order))
                save_data(items)
                refresh_list()
                update_selected_panel()
                popup.destroy()
            else:
                messagebox.showwarning("Warning", "Text cannot be empty.")
        
        def delete_item_popup():
            if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this item?"):
                items.remove(item_text)
                # Remove from selected items if it was selected
                if item_text in [item[0] for item in selected_items]:
                    selected_items.discard(next(item for item in selected_items if item[0] == item_text))
                save_data(items)
                refresh_list()
                update_selected_panel()
                popup.destroy()
        
        # Add buttons
        button_frame = tk.Frame(popup)
        button_frame.pack(pady=10)
        
        save_btn = tk.Button(button_frame, text="Save Changes", command=save_changes)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        delete_btn = tk.Button(button_frame, text="Delete Item", command=delete_item_popup)
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(button_frame, text="Cancel", command=popup.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)

def refresh_list(display_items=None, display_indices=None):
    """Refresh the listbox with updated items."""
    if display_items is None:
        display_items = items
        display_indices = list(range(len(items)))
        
    for widget in items_frame.winfo_children():
        widget.destroy()
    
    check_vars.clear()
    
    for i, (item, orig_index) in enumerate(zip(display_items, display_indices)):
        var = tk.BooleanVar()
        # Set checkbox state based on whether item is in selected_items
        if item in [x[0] for x in selected_items]:
            var.set(True)
        checkbox = tk.Checkbutton(items_frame, text=item, variable=var, 
                                command=lambda idx=orig_index, v=var: toggle_item(idx, v))
        checkbox.pack(anchor="w")
        # Bind double-click event
        checkbox.bind('<Double-Button-1>', on_double_click)
        check_vars.append(var)



# Initialize main app window
root = tk.Tk()
root.title("Clipboard Data App")
root.geometry("800x700")
root.configure(bg="#f0f0f0")

# Initialize variables
items = load_data()
selected_items = set()
check_vars = []

# Create main frames
input_frame = tk.Frame(root, bg="#f0f0f0")
input_frame.pack(pady=10, padx=10, fill="x")

# Create list frame with scrollbar - height limited to show ~8 items
list_frame = tk.Frame(root, bg="white", bd=2, relief="groove", height=200)  # Set fixed height
list_frame.pack(pady=10, padx=10, fill="x")  # Changed fill to x only
list_frame.pack_propagate(False)  # Prevent frame from expanding

# Add search bar
search_frame = tk.Frame(list_frame, bg="#f8f9fa", bd=2, relief="groove")
search_frame.pack(fill="x", padx=10, pady=8)

search_label = tk.Label(search_frame, text="Search:", bg="#f8f9fa", 
                       font=("Arial", 11, "bold"), fg="#2c3e50")
search_label.pack(side="left", padx=8)

search_var = tk.StringVar()
search_var.trace("w", lambda name, index, mode: search_items())

search_entry = tk.Entry(search_frame, textvariable=search_var, width=40,
                       font=("Arial", 10), bd=2, relief="solid",
                       bg="white", fg="#2c3e50",
                       insertbackground="#2c3e50")  # Cursor color
search_entry.pack(side="left", padx=8, pady=6)

# Add a subtle border effect on focus
def on_focus_in(event):
    event.widget.configure(relief="solid", bd=2)
def on_focus_out(event):
    event.widget.configure(relief="solid", bd=2)

search_entry.bind("<FocusIn>", on_focus_in)
search_entry.bind("<FocusOut>", on_focus_out)

# Create canvas and scrollbar
canvas = tk.Canvas(list_frame, bg="white")
scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
items_frame = tk.Frame(canvas, bg="white")

# Configure canvas
canvas.configure(yscrollcommand=scrollbar.set)

# Pack scrollbar and canvas
scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)

# Create window in canvas for items
canvas_window = canvas.create_window((0, 0), window=items_frame, anchor="nw")

# Configure canvas scrolling
def configure_scroll_region(event):
    canvas.configure(scrollregion=canvas.bbox("all"))
items_frame.bind("<Configure>", configure_scroll_region)

# Configure canvas width
def configure_canvas_width(event):
    canvas.itemconfig(canvas_window, width=event.width)
canvas.bind("<Configure>", configure_canvas_width)

# Add mouse wheel scrolling
def on_mousewheel(event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
canvas.bind_all("<MouseWheel>", on_mousewheel)

# Clear checkboxes button
clear_button = tk.Button(root, text="Clear Selection", command=clear_checkboxes,
                        bg="#ff6b6b", fg="white", font=("Arial", 10, "bold"),
                        width=15, relief="raised")
clear_button.pack(pady=5)

selected_frame = tk.Frame(root, bg="#f0f0f0")
selected_frame.pack(pady=10, padx=10, fill="x")

# Input box with label
input_label = tk.Label(input_frame, text="Enter Text:", font=("Arial", 10, "bold"), bg="#f0f0f0")
input_label.pack(anchor="w")

input_box = tk.Text(input_frame, height=4, width=60, font=("Arial", 10), bd=2, relief="groove")
input_box.pack(pady=(5, 10))

add_button = tk.Button(input_frame, text="Add Text", command=add_text, 
                      bg="#4CAF50", fg="white", font=("Arial", 10, "bold"),
                      width=15, relief="raised")
add_button.pack()

# Selected text panel with buttons
selected_label = tk.Label(selected_frame, text="Selected Text:", 
                         font=("Arial", 12, "bold"), bg="#f0f0f0")
selected_label.pack(anchor="w")

button_frame = tk.Frame(selected_frame, bg="#f0f0f0")
button_frame.pack(fill="x", pady=5)

selected_panel = tk.Text(selected_frame, height=15, width=60, 
                        font=("Arial", 10), state="disabled",
                        bd=2, relief="groove")
selected_panel.pack(pady=(5, 10))

copy_button = tk.Button(button_frame, text="Copy!", command=copy_selected_text,
                       bg="#4CAF50", fg="white", font=("Arial", 10, "bold"),
                       width=15, relief="raised")
copy_button.pack(side="right")

# Populate the list
refresh_list()

# Run the app
root.mainloop()
