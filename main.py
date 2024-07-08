import os
import shutil
import json
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import mysql.connector

class ImageUploader(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Image Uploader")
        self.geometry("700x500")
        self.images = [None, None, None]
        self.image_labels = [tk.Label(self) for _ in range(3)]
        self.image_paths = [None, None, None]

        self.create_widgets()
        self.connect_db()

    def connect_db(self):
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="mysql",
            database="mydatabase"
        )
        self.cursor = self.db.cursor()
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS uploads (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255),
            description TEXT,
            image1 VARCHAR(255),
            image2 VARCHAR(255),
            image3 VARCHAR(255)
        )
        """)

    def create_widgets(self):
        # Title
        self.title_label = tk.Label(self, text="Title:")
        self.title_label.pack()
        self.title_entry = tk.Entry(self, width=50)
        self.title_entry.pack()

        # Description
        self.description_label = tk.Label(self, text="Description:")
        self.description_label.pack()
        self.description_text = tk.Text(self, height=5, width=50)
        self.description_text.pack()

        # Image upload buttons
        self.upload_frame = tk.Frame(self)
        self.upload_frame.pack()
        for i in range(3):
            self.image_labels[i] = tk.Label(self.upload_frame)
            self.image_labels[i].grid(row=0, column=i, padx=5, pady=5)
            self.image_labels[i].bind("<Button-1>", lambda e, i=i: self.view_uploaded_image(i))
            upload_button = tk.Button(self.upload_frame, text=f"Upload Image {i + 1}", command=lambda i=i: self.upload_image(i))
            upload_button.grid(row=1, column=i, padx=5, pady=5)

        # Save button
        self.save_button = tk.Button(self, text="Save", command=self.save_data)
        self.save_button.pack(pady=10)

        # View button
        self.view_button = tk.Button(self, text="View Saved Data", command=self.view_data)
        self.view_button.pack()

        # View Uploaded Images button
        self.view_uploaded_button = tk.Button(self, text="View Uploaded Images", command=self.view_uploaded_images)
        self.view_uploaded_button.pack(pady=10)

    def upload_image(self, index):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp;*.gif")])
        if file_path:
            # Check if the image is already uploaded
            if file_path in self.image_paths:
                messagebox.showerror("Error", "This image is already uploaded.")
                return
            
            self.image_paths[index] = file_path
            img = Image.open(file_path)
            img.thumbnail((100, 100))
            self.images[index] = ImageTk.PhotoImage(img)
            self.image_labels[index].config(image=self.images[index])

    def save_data(self):
        title = self.title_entry.get()
        description = self.description_text.get("1.0", tk.END).strip()
        if not title or not description or None in self.image_paths:
            messagebox.showerror("Error", "Please fill in all fields and upload all images.")
            return

        data_folder = "data"
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)

        save_folder = os.path.join(data_folder, title)
        if os.path.exists(save_folder):
            messagebox.showerror("Error", "Title already exists. Please enter a new title.")
            return

        os.makedirs(save_folder)

        # Save title and description in JSON
        data = {
            "title": title,
            "description": description
        }
        with open(os.path.join(save_folder, "data.json"), "w") as file:
            json.dump(data, file, indent=4)

        # Save images
        image_filenames = []
        for i, image_path in enumerate(self.image_paths):
            img = Image.open(image_path)
            image_filename = f"image_{i + 1}.png"
            img.save(os.path.join(save_folder, image_filename))
            image_filenames.append(image_filename)

        # Clear input fields and images
        self.title_entry.delete(0, tk.END)
        self.description_text.delete("1.0", tk.END)
        for i in range(3):
            self.image_labels[i].config(image='')
            self.images[i] = None
            self.image_paths[i] = None

        # Save to MySQL database
        self.cursor.execute("""
        INSERT INTO uploads (title, description, image1, image2, image3)
        VALUES (%s, %s, %s, %s, %s)
        """, (title, description, image_filenames[0], image_filenames[1], image_filenames[2]))
        self.db.commit()

        messagebox.showinfo("Success", "Data saved successfully!")

    def view_data(self):
        view_window = tk.Toplevel(self)
        view_window.title("View Saved Data")

        # Create a canvas with a vertical scrollbar
        canvas = tk.Canvas(view_window)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(view_window, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        canvas.configure(yscrollcommand=scrollbar.set)

        # Create a frame inside the canvas to hold the data
        frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=frame, anchor=tk.NW)

        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        frame.bind("<Configure>", on_configure)

        def refresh_data():
            for widget in frame.winfo_children():
                widget.destroy()
            display_data()

        def display_data():
            self.cursor.execute("SELECT id, title, description, image1, image2, image3 FROM uploads ORDER BY id")
            rows = self.cursor.fetchall()

            if not rows:
                messagebox.showerror("Error", "No data available to view.")
                return

            for row in rows:
                id, title, description, image1, image2, image3 = row
                data_frame = tk.Frame(frame)
                data_frame.pack(pady=10, padx=10, fill='x')

                # Title
                title_label = tk.Label(data_frame, text="Title:")
                title_label.pack(side=tk.TOP, anchor='center')
                title_entry = tk.Entry(data_frame, width=50)
                title_entry.insert(0, title)
                title_entry.pack(pady=5, fill='x', anchor='center')

                # Description
                description_label = tk.Label(data_frame, text="Description:")
                description_label.pack(side=tk.TOP, anchor='center')
                description_entry = tk.Text(data_frame, height=5, width=50)
                description_entry.insert(tk.END, description)
                description_entry.pack(pady=5, fill='x', anchor='center')

                # ID
                id_label = tk.Label(data_frame, text="Place Priority Data:")
                id_label.pack(side=tk.TOP, anchor='center')
                id_entry = tk.Entry(data_frame, width=5)
                id_entry.insert(0, str(id))
                id_entry.pack(pady=5, side=tk.TOP, anchor='center')

                # Update button
                update_button = tk.Button(data_frame, text="Save Updated Data", command=lambda id=id, id_entry=id_entry, title_entry=title_entry, description_entry=description_entry: update_data(id, title, description, id_entry, title_entry, description_entry))
                update_button.pack(pady=5, side=tk.TOP, anchor='center')

                # Images
                images_frame = tk.Frame(data_frame)
                images_frame.pack(pady=5)

                image_paths = [image1, image2, image3]
                for i, image_filename in enumerate(image_paths):
                    if image_filename:
                        image_path = os.path.join("data", title, image_filename)
                        if os.path.exists(image_path):
                            img = Image.open(image_path)
                            img.thumbnail((100, 100))
                            img = ImageTk.PhotoImage(img)
                            img_label = tk.Label(images_frame, image=img)
                            img_label.image = img
                            img_label.pack(side=tk.LEFT, padx=5, pady=5)
                            img_label.bind("<Button-1>", lambda e, image_path=image_path: self.view_image(image_path))

                # Delete button
                delete_button = tk.Button(data_frame, text="Delete", command=lambda id=id, title=title, data_frame=data_frame: self.delete_data(id, title, data_frame))
                delete_button.pack(pady=5, anchor='center')

        def update_data(id, title, description, id_entry, title_entry, description_entry):
            new_id_str = id_entry.get()
            new_title = title_entry.get()
            new_description = description_entry.get("1.0", tk.END).strip()

            if not new_id_str.isdigit():
                messagebox.showerror("Error", "ID must be a number.")
                return
            new_id = int(new_id_str)

            if new_id != id:
                self.cursor.execute("SELECT COUNT(*) FROM uploads WHERE id = %s", (new_id,))
                count = self.cursor.fetchone()[0]
                if count > 0:
                    messagebox.showerror("Error", "ID already exists. Please enter a unique ID.")
                    return

            try:
                self.cursor.execute("UPDATE uploads SET id = %s, title = %s, description = %s WHERE id = %s", (new_id, new_title, new_description, id))
                self.db.commit()
                # Update the local JSON file
                old_folder_path = os.path.join("data", title)
                new_folder_path = os.path.join("data", new_title)
                if old_folder_path != new_folder_path:
                    os.rename(old_folder_path, new_folder_path)
                data = {
                    "title": new_title,
                    "description": new_description
                }
                with open(os.path.join(new_folder_path, "data.json"), "w") as file:
                    json.dump(data, file, indent=4)
                messagebox.showinfo("Success", "Data updated successfully!")
                refresh_data()
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Failed to update data: {err}")

        display_data()

        # Bind the MouseWheel event to the canvas for scrollwheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(-1 * int((event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def delete_data(self, id, title, frame):
        if messagebox.askyesno("Delete", "Are you sure you want to delete this data?"):
            # Delete from MySQL database
            self.cursor.execute("DELETE FROM uploads WHERE id = %s", (id,))
            self.db.commit()

            # Delete locally
            folder_path = os.path.join("data", title)
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)
            frame.destroy()

            messagebox.showinfo("Success", "Data deleted successfully!")

    def view_uploaded_images(self):
        if None in self.image_paths:
            messagebox.showerror("Error", "Please upload all images before viewing.")
            return

        view_window = tk.Toplevel(self)
        view_window.title("View Uploaded Images")

        for i, image_path in enumerate(self.image_paths):
            if image_path:
                img = Image.open(image_path)
                img.thumbnail((200, 200))
                img = ImageTk.PhotoImage(img)
                img_label = tk.Label(view_window, image=img)
                img_label.image = img
                img_label.grid(row=0, column=i, padx=10, pady=10)

    def view_uploaded_image(self, index):
        if self.images[index]:
            view_window = tk.Toplevel(self)
            view_window.title(f"View Image {index + 1}")

            img = Image.open(self.image_paths[index])
            img = ImageTk.PhotoImage(img)
            img_label = tk.Label(view_window, image=img)
            img_label.image = img
            img_label.pack(padx=10, pady=10)
        else:
            messagebox.showerror("Error", f"Image {index + 1} not uploaded yet.")

    def view_image(self, image_path):
        view_window = tk.Toplevel(self)
        view_window.title("View Image")

        img = Image.open(image_path)
        img = ImageTk.PhotoImage(img)
        img_label = tk.Label(view_window, image=img)
        img_label.image = img
        img_label.pack(padx=10, pady=10)

if __name__ == "__main__":
    app = ImageUploader()
    app.mainloop()
