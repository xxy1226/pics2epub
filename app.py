import os
from ebooklib import epub

import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

# from model import ImageToEPUBModel
# from view import ImageToEPUBView

from PIL import Image, ImageTk

class ImageToEPUBModel:
  def __init__(self):
    self.folder_path = ""
    self.image_files = []
    self.cover_image = None

  def load_images(self, folder_path):
    # 加载文件夹中的图片
    self.folder_path = folder_path
    self.image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
    self.image_files.sort()

  def generate_epub(self, output_path, title, author, cover_path=None):
    # 生成EPUB文件
    book = epub.EpubBook()
    book.set_title(title)
    book.set_identifier(title)
    book.set_language("en")
    book.add_author(author)

    if cover_path:
      book.set_cover(cover_path, open(os.path.join(self.folder_path, cover_path), 'rb').read())

    chapter = epub.EpubHtml(title=title, file_name=f"chapter.xhtml", lang="en")
    chapter.content=u'<html><head></head><body>'
    for i, img_name in enumerate(self.image_files):
      img_path = os.path.join(self.folder_path, img_name)
      image_content = open(img_path, 'rb').read()
      img = epub.EpubImage(uid=f'image_{img_name}', file_name=os.path.join('static', img_name), media_type=f'image/{img_name.split(".")[-1]}', content=image_content)
      chapter.content += f'<br><img src="{os.path.join("static", img_name)}" alt="{img_name}"><p>Image {i+1}: {img_name}</p>'
      book.add_item(img)
    chapter.content += u'</body></html>'

    book.add_item(chapter)
    book.toc = (epub.Link('chapter.xhtml', 'Collection', 'Collection'),)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    print("cover: ", cover_path)
    book.spine = ['cover', chapter] if cover_path else [chapter]
    # book.spine = [chapter]
    epub.write_epub(output_path, book)

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
      self.cover_image = self.image_listbox.get(selected_index)
      self.show_image_preview()

  def show_image_preview(self):
    img = Image.open(os.path.join(self.controller.model.folder_path, self.cover_image))
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
    self.cover_image = self.image_listbox.get(0)

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
    self.image_label.config(image=None)
    self.image_label.config(bg="white")
    self.image_label.config(text="图片预览区域")
    self.image_label.image = None
    self.controller.model.folder_path = ""  # 清空文件夹路径
    self.controller.model.image_files = []  # 清空图片列表

class ImageToEPUBController:
  def __init__(self, root):
    self.model = ImageToEPUBModel()
    self.view = ImageToEPUBView(root, self)

  def on_folder_selected(self):
    # 处理文件夹选择事件
    folder_path = filedialog.askdirectory(title="选择包含图片的文件夹")
    if folder_path:
      self.model.load_images(folder_path)
      self.view.update_image_list(self.model.image_files)

      # 获取文件夹名称并设置为书名
      folder_name = os.path.basename(folder_path)
      self.view.set_title(folder_name)

  def on_generate_epub(self):
    # 处理生成EPUB事件
    if not self.model.folder_path or not self.model.image_files:
      messagebox.showwarning("警告", "请先选择包含图片的文件夹！")
      return

    # 获取书名
    title = self.view.get_book_name()

    if not title:
      messagebox.showwarning("警告", "请输入书名！")
      return

    # 获取作者信息
    author = self.view.get_author()

    # 创建封面
    cover_path = None
    if len(self.view.cover_checkbutton.state()) and self.view.cover_checkbutton.state()[0]=='selected':
      cover_path = self.view.cover_image

    output_path = filedialog.asksaveasfilename(defaultextension=".epub", filetypes=[("EPUT files", "*.epub")], initialfile=f"{title}.epub")
    if output_path:
      try:
        self.model.generate_epub(output_path, title, author, cover_path=cover_path)
        messagebox.showinfo("成功", f"EPUB文件已生成：{output_path}")
      except Exception as e:
        messagebox.showerror("错误", f"生成EPUB文件时出错： {str(e)}")
      finally:
        self.view.clear_all()

if __name__ == "__main__":
  root = tk.Tk()
  root.title("PICS2EPUB")
  root.geometry("1024x768")
  app = ImageToEPUBController(root)
  root.mainloop()