import os
import frontmatter
from slugify import slugify
from markdown2 import markdown
from jinja2 import Environment, FileSystemLoader
import htmlmin
from bs4 import BeautifulSoup
import shutil
from json import load

env = Environment(loader=FileSystemLoader(searchpath="./templates"))


# The generator Class
class StaticSiteGenerator:
    def generateAssets(self):
        shutil.copytree('assets', 'dist/assets')

    def generateIndex(self, context):
        index_template = env.get_template("index.html")
        with open("dist/index.html", "w") as index_file:
            index_file.write(index_template.render(context=context))

    def _load_data(self):
        context = {}
        pages = self._load_pages()
        config = self._load_config()

        context.setdefault("pages", pages)
        context.setdefault("config", config)
        return context

    def _load_config(self):
        with open('user.conf.json') as user_config:
            return load(user_config)

    def _load_pages(self):
        pages_list = [
            page
            for page in os.listdir("content/pages")
            if os.path.isfile(os.path.join(f"content/pages/{page}"))
        ]
        pages = []
        for page in pages_list:
            with open(f"content/pages/{page}") as md_page:
                md = frontmatter.load(md_page)
                md.metadata["slug"] = slugify(md.metadata["title"])
                pages.append(
                    {"metadata": md.metadata,
                     "content": markdown(md.content, extras=['code-friendly','fenced-code-blocks'])
                     }
                )
        return pages
    # def _set_sections_tags(self, md_content):
    #     soup = BeautifulSoup(md_content, "html.parser")
    #     toc = {tag.text: f"#{slugify(tag.text)}" for tag in soup.find_all("h2")}
    #     for h2 in soup.find_all("h2"):
    #         h2.attrs["id"] = slugify(h2.text)
    #     return str(soup.prettify()), toc

    def generatePages(self, context):
        os.makedirs("dist/blog", exist_ok=True)
        for article in context['pages']:
            page_tempate = env.get_template("post.html")
            with open(f"dist/blog/{article['metadata']['slug']}.html", "w") as post_html:
                post_html.write(page_tempate.render(article=article, context=context))
    # def generateTags(self):
    #     # Momo
    #     pages_data=self._load_pages()
    #     tags = set()
    #     for page in pages_data:
    #         tags.update(page['metadata']['tags'])
    #     os.makedirs('dist/tags',exist_ok=True)
    #     for tag in tags:
    #         tag_template=env.get_template('tag.html')
    #         with open(f'dist/tags/{slugify(tag)}.html', 'w') as tag_html:
    #             tag_html.write(tag_template.render(
    #                 tag=tag,
    #                 pages=pages_data
    #             ))
    def generateBlogPage(self, context):
        blog_template = env.get_template("blog.html")
        with open("dist/blog/index.html", "w") as blog_html:
            blog_html.write(blog_template.render(context=context))

    def generate(self):
        shutil.rmtree('dist', ignore_errors=True)
        self.generateAssets()
        context = self._load_data()
        self.generateIndex(context=context)
        self.generatePages(context=context)
        self.generateBlogPage(context=context)
        # self.generateTags()


if __name__ == "__main__":
    StaticSiteGenerator().generate()
