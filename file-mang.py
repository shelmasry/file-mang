import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

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

        # إطار التفاصيل
        self.detail_frame = tk.Frame(self.main_frame, padx=10)
        self.detail_frame.pack(side=tk.RIGHT, fill=tk.Y)

        self.details_label = tk.Label(self.detail_frame, text="Project Details", font=("Arial", 14, "bold"))
        self.details_label.pack(anchor="n", pady=5)

        self.details_text = tk.Text(self.detail_frame, wrap=tk.WORD, height=25, width=40)
        self.details_text.pack(fill=tk.BOTH, expand=True)

        # أزرار التحكم
        self.button_frame = tk.Frame(root, pady=10)
        self.button_frame.pack(fill=tk.X)

        self.create_project_button = tk.Button(self.button_frame, text="Create Project", command=self.create_project)
        self.create_project_button.pack(side=tk.LEFT, padx=5)

        self.add_folder_button = tk.Button(self.button_frame, text="Add Folder", command=self.add_folder)
        self.add_folder_button.pack(side=tk.LEFT, padx=5)

        self.add_file_button = tk.Button(self.button_frame, text="Add File", command=self.add_file)
        self.add_file_button.pack(side=tk.LEFT, padx=5)

        self.add_directory_button = tk.Button(self.button_frame, text="Add Directory", command=self.add_directory)
        self.add_directory_button.pack(side=tk.LEFT, padx=5)

        self.retrieve_file_button = tk.Button(self.button_frame, text="Retrieve File", command=self.retrieve_file)
        self.retrieve_file_button.pack(side=tk.LEFT, padx=5)

        self.refresh_tree_button = tk.Button(self.button_frame, text="Refresh Tree", command=self.refresh_tree)
        self.refresh_tree_button.pack(side=tk.LEFT, padx=5)

        self.delete_project_button = tk.Button(self.button_frame, text="Delete Project", command=self.delete_project)
        self.delete_project_button.pack(side=tk.LEFT, padx=5)

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

    def create_project(self):
        project_name = simpledialog.askstring("Input", "Enter project name:", parent=self.root)
        if project_name:
            project_path = os.path.join(self.base_directory, project_name)
            os.makedirs(project_path, exist_ok=True)
            messagebox.showinfo("Success", f"Project '{project_name}' created!")
            self.refresh_tree()

    def add_folder(self):
        selected_item = self.tree.selection()
        if selected_item:
            parent_path = self.get_full_path_from_tree(selected_item)
            folder_name = simpledialog.askstring("Input", "Enter folder name:", parent=self.root)
            if folder_name:
                os.makedirs(os.path.join(parent_path, folder_name), exist_ok=True)
                messagebox.showinfo("Success", f"Folder '{folder_name}' added!")
                self.refresh_tree()

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

    def retrieve_file(self):
        selected_item = self.tree.selection()
        if selected_item:
            file_path = self.get_full_path_from_tree(selected_item)
            if os.path.isfile(file_path):
                target_path = filedialog.askdirectory(title="Select Target Directory")
                if target_path:
                    shutil.copy(file_path, target_path)
                    messagebox.showinfo("Success", "File retrieved successfully!")

    def delete_project(self):
        selected_item = self.tree.selection()
        if selected_item:
            item_path = self.get_full_path_from_tree(selected_item)
            if os.path.exists(item_path):
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
                messagebox.showinfo("Success", "Item deleted!")
                self.refresh_tree()

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
