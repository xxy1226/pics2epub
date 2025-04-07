# -*- coding: utf-8 -*-

import os
from ebooklib import epub
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk

# import ebooklib

default_page = """
<html>
<head />
<body>
  {body_content}
</body>
</html>
      """

class ImageToEPUBModel:
  def __init__(self):
    self.folder_path = ""
    self.toc = []
    self.sections = []
    self.book = None
    self.item_count = 1
    self.page_count = 1
    

  def load_images(self, folder_path):
    """加载文件夹中的图片，包括子文件夹"""
    self.folder_path = folder_path

    # 遍历主文件夹中的图片
    image_files = self.get_images_in_folder(folder_path)
    if len(image_files):
      self.sections.append({os.path.basename(folder_path):image_files})

    # 遍历子文件夹
    for subfolder in sorted(os.listdir(folder_path)):
      subfolder_path = os.path.join(folder_path, subfolder)
      if os.path.isdir(subfolder_path):
        image_files = self.get_images_in_folder(subfolder_path, True)
        if image_files:
          self.sections.append({subfolder:image_files})

  def get_images_in_folder(self, folder_path, subfolder=False):
    """返回文件夹中的图片文件列表。如果子文件夹为真，则返回 子文件夹名/图片名 列表"""
    if subfolder:
      return [os.path.join(os.path.basename(folder_path), f) for f in sorted(os.listdir(folder_path)) if f.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'bmp'))]
    return [f for f in sorted(os.listdir(folder_path)) if f.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'bmp'))]
  
  def generate_epub(self, output_path, title, author, pagination=True, cover_path=None):
    """生成EPUB文件"""
    self.book = epub.EpubBook()
    self.book.set_title(title)
    self.book.set_identifier(title)
    self.book.set_language("en")
    self.book.add_author(author)
    self.book.spine = ['nav']

    # 添加封面
    if cover_path:
      cover_image = open(cover_path, 'rb').read()
      cover_image_name = os.path.basename(cover_path)
      self.book.set_cover(f"Cover/{cover_image_name}", cover_image)
      self.book.spine = ['cover', 'nav']

    for section in self.sections:
      section_name, images = next(iter(section.items()))

      if not pagination is None:
        self.book_add_per_page(section_name, images)
      else:
        self.book_add_one_page(section_name, images)

    # 添加目录
    style = '''
body {
    font-family: Cambria, Liberation Serif, Bitstream Vera Serif, Georgia, Times, Times New Roman, serif;
}

h2 {
     text-align: left;
     text-transform: uppercase;
     font-weight: 200;     
}

ol {
        list-style-type: none;
}

ol > li:first-child {
        margin-top: 0.3em;
}


nav[epub|type~='toc'] > ol > li > ol  {
    list-style-type:square;
}


nav[epub|type~='toc'] > ol > li > ol > li {
        margin-top: 0.3em;
}

'''

    # 加入 css
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    self.book.add_item(nav_css)

    self.book.toc = self.toc
    self.book.add_item(epub.EpubNcx())
    self.book.add_item(epub.EpubNav())

    # 捉虫用
    # items = self.book.get_items()
    # if items:
    #   for item in items:
    #     if item.get_type() == ebooklib.ITEM_DOCUMENT:
    #       print('===========================')
    #       print('NAME: ', item.get_name())
    #       print('---------------------------')
    #       print(item.get_content())
    #       print('===========================')
    # book_images = self.book.get_items_of_type(ebooklib.ITEM_IMAGE)
    # print("Images:")
    # for image in book_images:
    #   print(image)

    # 生成书籍
    epub.write_epub(output_path, self.book, {})

  def book_add_per_page(self, section_name, images):
    """每一页一张图片"""
    clean_section_name = "".join(c if c.isalnum() else "_" for c in section_name)

    for i, image in enumerate(images):
      # 将图片添加到 EPUB 中
      image_file_path = os.path.join(self.folder_path, image)
      image_data = open(image_file_path, 'rb').read()
      image_name = os.path.basename(image)
      ext = image_name.split('.')[-1].lower()
      image_item = epub.EpubImage(
        uid=f'item{self.item_count}',
        file_name=f"{clean_section_name}/{image_name}",
        media_type=f"image/{ext}" if ext in ['png', 'gif', 'bmp'] else 'image/jpeg',
        content=image_data,
      )
      self.book.add_item(image_item)
      # 创建 HTML 内容
      chapter_title = f'page{self.item_count}'
      chapter_name = f'{chapter_title}.xhtml'
      chapter = epub.EpubHtml(
        title=chapter_title,
        file_name=chapter_name,
        lang='en'
      )
      body_content = f"""
  <div style="text-align: center;">
    <img src="{clean_section_name}/{image_name}" alt="{image_name}" style="max-width: 100%; height: auto;" >
  </div>
      """
      chapter.content = default_page.format(body_content=body_content)
      self.book.add_item(chapter)
      self.book.spine.append(chapter)
      self.item_count += 1
      if not i:
        self.toc.append(epub.Link(chapter_name, section_name, clean_section_name))

  def book_add_one_page(self, section_name, images):
    """每一页一个文件夹的图片"""
    clean_section_name = "".join(c if c.isalnum() else "_" for c in section_name)
    
    chapter_title = f'page{self.page_count}'
    chapter_name = f'{chapter_title}.xhtml'
    chapter = epub.EpubHtml(
      title=chapter_title,
      file_name=chapter_name,
      lang='en'
    )
    body_content = ""

    for i, image in enumerate(images):
      # 将图片添加到 EPUB 中
      image_file_path = os.path.join(self.folder_path, image)
      image_data = open(image_file_path, 'rb').read()
      image_name = os.path.basename(image)
      ext = image_name.split('.')[-1].lower()
      image_item = epub.EpubImage(
        uid=f'item{self.item_count}',
        file_name=f"{clean_section_name}/{image_name}",
        media_type=f"image/{ext}" if ext in ['png', 'gif', 'bmp'] else 'image/jpeg',
        content=image_data,
      )
      self.book.add_item(image_item)
      # 创建 HTML 内容
      body_content += f"""
  <div style="text-align: center;">
    <img src="{clean_section_name}/{image_name}" alt="{image_name}" style="max-width: 100%; height: auto;" >
  </div>
      """
      self.item_count += 1

    chapter.content = default_page.format(body_content=body_content)
    self.book.add_item(chapter)
    self.book.spine.append(chapter)
    self.toc.append(epub.Link(chapter_name, section_name, clean_section_name))
    self.page_count +=1

  def clear_model(self):
    self.folder_path = ""
    self.toc = []
    self.sections = []
    self.book = None
    self.item_count = 1
    self.page_count = 1

class ImageToEPUBView:
  def __init__(self, root:tk.Tk, controller):
    self.root = root
    self.controller = controller
    self.folder_indexes = [] # 记录文件夹的索引
    self.selected_index = 1 # 记录选中的图片，之后作为封面使用

    # 文件夹选择按钮
    self.folder_button = ttk.Button(root, text="选择文件夹", command=self.controller.on_folder_selected)
    self.folder_button.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

    self.app_description = tk.Label(root, text="双击列表中的文件名以预览图片。如果勾选[创建封面]选项，则高亮的图片将作为封面图片，若没有高亮的图片，则第一张图片将作为封面图片。")
    self.app_description.grid(row=1, column=0, columnspan=6, padx=(10, 5), pady=0, sticky="w")

    self.image_listbox = tk.Listbox(root)
    self.image_listbox.grid(row=2, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
    self.image_listbox.bind("<<ListboxSelect>>", self.on_image_select)

    # 图片预览
    self.image_view = tk.Label(root, bg="white", text="图片预览区域")
    self.image_view.grid(row=2, column=4, columnspan=2, padx=10, pady=10, sticky="nsew")

    # 创建封面按钮
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

    # 分页按钮
    self.pagination_checkbutton = ttk.Checkbutton(root, text='一页一图')
    self.pagination_checkbutton.grid(row=4, column=1, padx=(0, 10), pady=5, sticky="e")
    self.pagination_checkbutton.state(['!alternate'])
    self.pagination_checkbutton.state(['selected']) # ('alternate',) ('selected',) ()

    # 生成EPUB按钮
    self.generate_button = ttk.Button(root, text="生成EPUB", command=self.controller.on_generate_epub)
    self.generate_button.grid(row=5, column=0, columnspan=6, padx=10, pady=10, sticky="ew")
    
    # 设置网络布局的权重
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=4)  
    root.grid_columnconfigure(2, weight=1)  
    root.grid_columnconfigure(3, weight=5)  
    root.grid_columnconfigure(4, weight=1)  
    root.grid_columnconfigure(5, weight=3) 
    root.grid_rowconfigure(2, weight=1)     # 图片列表区域占据更多空间

  def update_image_list(self, image_files):
    # 更新图片列表
    self.image_listbox.delete(0, tk.END)
    count = 0

    for i, collection in enumerate(image_files):
      section, files = next(iter(collection.items()))
      self.image_listbox.insert(tk.END, section)
      self.image_listbox.itemconfig(tk.END, {'fg': 'gray'}) # 字体变灰
      self.folder_indexes.append(count)
      count += 1
      for file in files:
        self.image_listbox.insert(tk.END, file)
        count += 1

  def set_title(self, title):
    """设置书名"""
    self.title_entry.delete(0, tk.END)
    self.title_entry.insert(0, title)

  def get_book_name(self):
    return self.title_entry.get()

  def get_author(self):
    return self.author_entry.get()
  
  def get_cover_image(self):
    selected_index = self.image_listbox.curselection()[0] if len(self.image_listbox.curselection()) else 1
    return self.image_listbox.get(selected_index)
  
  def on_image_select(self, event):
    selected_index = self.image_listbox.curselection()
    if selected_index and selected_index[0] not in self.folder_indexes:
      self.selected_index = selected_index[0]
      self.show_image_preview()
    else:
      self.image_listbox.select_clear(0, tk.END)
      self.image_listbox.selection_set(self.selected_index)

  def show_image_preview(self):
    img = Image.open(os.path.join(self.controller.model.folder_path, self.image_listbox.get(self.selected_index)))
    img.thumbnail((self.image_view.winfo_width(), self.image_view.winfo_height()))
    img_tk = ImageTk.PhotoImage(img)

    self.image_view.config(image=img_tk, bg="SystemButtonFace", text="")
    self.image_view.image = img_tk
  
  def clear_view(self):
    self.image_listbox.delete(0, tk.END)
    self.title_entry.delete(0, tk.END)
    self.author_entry.delete(0, tk.END)
    self.image_view.destroy()
    self.image_view = tk.Label(root, bg="white", text="图片预览区域")
    self.image_view.grid(row=2, column=4, columnspan=2, padx=10, pady=10, sticky="nsew")
    self.folder_indexes = []
    self.selected_index = 1

class ImageToEPUBController:
  def __init__(self, root):
    self.model = ImageToEPUBModel()
    self.view = ImageToEPUBView(root, self)

  def on_folder_selected(self):
    """打开包含图片的文件夹"""
    # 处理文件夹选择事件
    folder_path = filedialog.askdirectory(title="选择包含图片的文件夹")
    if folder_path:
      # 清除原有内容
      self.model.clear_model()
      self.view.clear_view()
      self.model.load_images(folder_path)
      self.view.update_image_list(self.model.sections)

      # 获取文件夹名称并设置为书名
      self.view.set_title(os.path.basename(folder_path))
    
  def on_generate_epub(self):
    """处理生成EPUB事件"""
    if not self.model.folder_path or self.view.image_listbox.size() < 2:
      messagebox.showwarning("警告", "请先选择包含图片的文件夹！\nfolder_path: "+ str(not self.model.folder_path))
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
      cover_path = os.path.join(self.model.folder_path, self.view.get_cover_image())

    # 是否每页一张图片
    pagination = False
    if len(self.view.pagination_checkbutton.state()) and self.view.pagination_checkbutton.state()[0]=='selected':
      pagination = True

    # 输出文件
    output_path = filedialog.asksaveasfilename(defaultextension=".epub", filetypes=[("EPUT files", "*.epub")], initialfile=f"{title}.epub")
    if output_path:
      try:
        self.model.generate_epub(output_path, title, author, pagination, cover_path)
        messagebox.showinfo("成功", f"EPUB文件已生成：{output_path}")
      except Exception as e:
        messagebox.showerror("错误", f"生成EPUB文件时出错：{str(e)}")
      else:
        self.view.clear_view()
        self.model.clear_model()

if __name__ == "__main__":
  root = tk.Tk()
  root.title('PIC2EPUB')
  root.geometry("1024x768")
  app = ImageToEPUBController(root)
  root.mainloop()