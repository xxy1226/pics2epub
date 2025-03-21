import os
from PIL import Image

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
      book.set_cover("cover.jpg", open(cover_path, 'rb').read())

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

    book.spine = ['cover', chapter] if cover else [chapter]
    epub.write_epub(output_path, book)
