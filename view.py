import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class ImageToEPUBView:
  def __init__(self, root, controller):
    self.root = root
    self.controller = controller
    self.cover_image = None

    # 文件夹选择按钮
    self.folder_button = ttk.Button(root, text="选择文件夹", command=self.controller.on_folder_selected)
    self.folder_button.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

    # 图片列表说明
    self.image_listbox_description = tk.Label(root, text = "双击列表中的文件名以预览图片。如果勾选[创建封面]选项，则高亮的图片将作为封面图片，若没有高亮的图片，则第一张图片将作为封面图片。")
    self.image_listbox_description.grid(row=1, column=0, columnspan=6, padx=(10, 5), pady=0, sticky="w")

    # 图片列表
    self.image_listbox = tk.Listbox(root)
    self.image_listbox.grid(row=2, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
    self.image_listbox.bind("<<ListboxSelect>>", self.on_image_select) # <Double-Button-1>

    # 图片预览
    self.image_label = tk.Label(root, bg="white", text="图片预览区域")
    self.image_label.grid(row=2, column=4, columnspan=2, padx=10, pady=10, sticky="nsew")

    # 创建封面
    self.cover_checkbutton = ttk.Checkbutton(root, text='创建封面')
    self.cover_checkbutton.grid(row=3, column=1, padx=(0, 10), pady=5, sticky="e")
    self.cover_checkbutton.state(['!alternate'])
    self.cover_checkbutton.state(['selected']) # ('alternate',) ('selected',) ()

    # 书名输入框
    self.title_label = ttk.Label(root, text="书名：")
    self.title_label.grid(row=3, column=2, padx=(10, 5), pady=5, sticky="e")
    self.title_entry = ttk.Entry(root)
    self.title_entry.grid(row=3, column=3, padx=(0, 10), pady=5, sticky="ew")

    # 作者输入框
    self.author_label = ttk.Label(root, text="作者：")
    self.author_label.grid(row=3, column=4, padx=(10, 5), pady=5, sticky="e")
    self.author_entry = ttk.Entry(root)
    self.author_entry.grid(row=3, column=5, padx=(0, 10), pady=5, sticky="ew")

    # 生成EPUB按钮
    self.generate_button = ttk.Button(root, text="生成EPUB", command=self.controller.on_generate_epub)
    self.generate_button.grid(row=4, column=0, columnspan=6, padx=10, pady=10, sticky="ew")

    # 设置网络布局的权重
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=4)  
    root.grid_columnconfigure(2, weight=1)  
    root.grid_columnconfigure(3, weight=5)  
    root.grid_columnconfigure(4, weight=1)  
    root.grid_columnconfigure(5, weight=3) 
    root.grid_rowconfigure(2, weight=1)     # 图片列表区域占据更多空间

  def on_image_select(self, event):
    selected_index = self.image_listbox.curselection()
    if selected_index:
      selected_image = self.image_listbox.get(selected_index)
      self.image_path = os.path.join(self.controller.model.folder_path, selected_image)
      self.show_image_preview()

  def show_image_preview(self):
    img = Image.open(self.image_path)
    img.thumbnail((self.image_label.winfo_width(), self.image_label.winfo_height()))
    img_tk = ImageTk.PhotoImage(img)
    
    self.image_label.config(image=img_tk)
    self.image_label.config(bg="SystemButtonFace")
    self.image_label.image = img_tk
    self.image_label.config(text="")

  def update_image_list(self, image_files):
    # 更新图片列表
    self.image_listbox.delete(0, tk.END)

    for i, file in enumerate(image_files):
      self.image_listbox.insert(tk.END, file)

  def get_cover_image(self):
    return self.cover_var.get()

  def set_title(self, title):
    """设置书名"""
    self.title_entry.delete(0, tk.END)
    self.title_entry.insert(0, title)

  def get_author(self):
    return self.author_entry.get()

  def get_book_name(self):
    return self.title_entry.get()

  def clear_all(self):
    self.image_listbox.delete(0, tk.END)
    self.title_entry.delete(0, tk.END)
    self.author_entry.delete(0, tk.END)
    self.controller.model.folder_path = ""  # 清空文件夹路径
    self.controller.model.image_files = []  # 清空图片列表
