import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from PyPDF2 import PdfReader

class ProjectManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Project Manager")
        self.root.geometry("900x600")
        self.base_directory = "projects"
        if not os.path.exists(self.base_directory):
            os.makedirs(self.base_directory)

        # الإطار الرئيسي
        self.main_frame = tk.Frame(root, padx=10, pady=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # شجرة المشاريع
        self.tree = ttk.Treeview(self.main_frame)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # شريط التمرير للشجرة
        self.tree_scroll = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree_scroll.pack(side=tk.LEFT, fill=tk.Y)
        self.tree.configure(yscrollcommand=self.tree_scroll.set)

        # إعداد أعمدة الشجرة
        self.tree["columns"] = ("Type", "Size")
        self.tree.column("#0", width=300, anchor="w")
        self.tree.heading("#0", text="Project/Folder/File")
        self.tree.column("Type", width=100, anchor="center")
        self.tree.heading("Type", text="Type")
        self.tree.column("Size", width=100, anchor="center")
        self.tree.heading("Size", text="Size (KB)")

        # حدث عند اختيار عنصر
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # إطار التفاصيل
        self.detail_frame = tk.Frame(self.main_frame, padx=10)
        self.detail_frame.pack(side=tk.RIGHT, fill=tk.Y)

        self.details_label = tk.Label(self.detail_frame, text="Details", font=("Arial", 14, "bold"))
        self.details_label.pack(anchor="n", pady=5)

        self.details_text = tk.Text(self.detail_frame, wrap=tk.WORD, height=25, width=40)
        self.details_text.pack(fill=tk.BOTH, expand=True)

        # أزرار التحكم
        self.button_frame = tk.Frame(root, pady=10)
        self.button_frame.pack(fill=tk.X)

        self.add_file_button = tk.Button(self.button_frame, text="Add File", command=self.add_file)
        self.add_file_button.pack(side=tk.LEFT, padx=5)

        self.add_directory_button = tk.Button(self.button_frame, text="Add Directory", command=self.add_directory)
        self.add_directory_button.pack(side=tk.LEFT, padx=5)

        self.refresh_tree_button = tk.Button(self.button_frame, text="Refresh Tree", command=self.refresh_tree)
        self.refresh_tree_button.pack(side=tk.LEFT, padx=5)

        # تحميل شجرة المشاريع
        self.refresh_tree()

    def refresh_tree(self):
        """إعادة تحميل شجرة المشاريع"""
        self.tree.delete(*self.tree.get_children())
        self.load_projects_to_tree()

    def load_projects_to_tree(self):
        """تحميل جميع المشاريع والفروع إلى الشجرة"""
        for project_name in os.listdir(self.base_directory):
            project_path = os.path.join(self.base_directory, project_name)
            if os.path.isdir(project_path):
                project_id = self.tree.insert("", "end", text=project_name, values=("Project", ""), open=True)
                self.load_folder_to_tree(project_path, project_id)

    def load_folder_to_tree(self, folder_path, parent_id):
        """تحميل المجلدات والملفات داخل الشجرة"""
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isdir(item_path):
                folder_id = self.tree.insert(parent_id, "end", text=item, values=("Folder", ""), open=False)
                self.load_folder_to_tree(item_path, folder_id)
            else:
                file_size = os.path.getsize(item_path) // 1024
                self.tree.insert(parent_id, "end", text=item, values=("File", file_size))

    def add_file(self):
        selected_item = self.tree.selection()
        if selected_item:
            parent_path = self.get_full_path_from_tree(selected_item)
            file_path = filedialog.askopenfilename(title="Select File to Add")
            if file_path:
                file_name = os.path.basename(file_path)
                target_path = os.path.join(parent_path, file_name)
                if os.path.exists(target_path):
                    new_name = f"copy_of_{file_name}"
                    target_path = os.path.join(parent_path, new_name)
                shutil.copy(file_path, target_path)
                messagebox.showinfo("Success", f"File '{file_name}' added!")
                self.refresh_tree()

    def add_directory(self):
        selected_item = self.tree.selection()
        if selected_item:
            parent_path = self.get_full_path_from_tree(selected_item)
            directory_path = filedialog.askdirectory(title="Select Directory to Add")
            if directory_path:
                directory_name = os.path.basename(directory_path)
                target_path = os.path.join(parent_path, directory_name)
                if os.path.exists(target_path):
                    directory_name = f"copy_of_{directory_name}"
                    target_path = os.path.join(parent_path, directory_name)
                shutil.copytree(directory_path, target_path)
                messagebox.showinfo("Success", f"Directory '{directory_name}' added!")
                self.refresh_tree()

    def on_tree_select(self, event):
        """عرض التفاصيل عند تحديد عنصر"""
        selected_item = self.tree.selection()
        if selected_item:
            item_path = self.get_full_path_from_tree(selected_item)
            if os.path.isdir(item_path):
                self.display_project_details(item_path)
            elif os.path.isfile(item_path) and item_path.endswith(".pdf"):
                self.display_pdf_content(item_path)

    def display_project_details(self, project_path):
        """عرض تفاصيل المشروع"""
        file_count = 0
        total_size = 0
        file_types = set()
        for root, _, files in os.walk(project_path):
            for file in files:
                file_count += 1
                total_size += os.path.getsize(os.path.join(root, file))
                file_types.add(file.split(".")[-1])

        details = f"Project: {os.path.basename(project_path)}\n"
        details += f"Number of Files: {file_count}\n"
        details += f"Total Size: {total_size // 1024} KB\n"
        details += f"File Types: {', '.join(file_types)}\n"

        self.details_text.delete("1.0", tk.END)
        self.details_text.insert(tk.END, details)

    def display_pdf_content(self, pdf_path):
        """عرض محتوى ملف PDF"""
        reader = PdfReader(pdf_path)
        content = ""
        for page in reader.pages:
            content += page.extract_text() + "\n"

        pdf_window = tk.Toplevel(self.root)
        pdf_window.title(f"PDF Content: {os.path.basename(pdf_path)}")
        pdf_text = tk.Text(pdf_window, wrap=tk.WORD)
        pdf_text.pack(fill=tk.BOTH, expand=True)
        pdf_text.insert(tk.END, content)

    def get_full_path_from_tree(self, selected_item):
        """استرجاع المسار الكامل للعنصر المحدد"""
        item_path = self.tree.item(selected_item, "text")
        parent_item = self.tree.parent(selected_item)
        while parent_item:
            parent_text = self.tree.item(parent_item, "text")
            item_path = os.path.join(parent_text, item_path)
            parent_item = self.tree.parent(parent_item)
        return os.path.join(self.base_directory, item_path)


if __name__ == "__main__":
    root = tk.Tk()
    app = ProjectManagerApp(root)
    root.mainloop()
