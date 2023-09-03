import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import frontmatter
import markdown2
from jinja2 import Environment, FileSystemLoader
from rich import print
from robyn import Request, Response, Robyn


@dataclass
class Post:
    id: int
    title: str
    date: str
    content: str


@dataclass
class Category:
    name: str
    posts: list[Post]


def get_content() -> list[Category]:
    content_root = Path("pages").resolve()
    content = []

    for category in content_root.iterdir():
        if category.is_dir():
            posts = []
            for post in category.iterdir():
                if post.is_file():
                    with open(post, "r") as f:
                        post_content = frontmatter.load(f)
                        posts.append(
                            Post(
                                title=post_content["title"],
                                date=post_content["date"],
                                id=post_content["id"],
                                content=markdown2.markdown(post_content.content),
                            )
                        )
            content.append(Category(name=category.name, posts=posts))

    return content


class Server(Robyn):
    def __init__(self):
        super().__init__(__file__)
        self.get("/")(self.index)
        self.get("/:category/:post_id")(self.content_handler)
        self.add_directory("/static", "public")
        self.content: list[Category] = get_content()
        self.env = Environment(loader=FileSystemLoader("templates"))
        print(self.content)

    async def static(self, request: Request) -> Response:
        print(request)
        return Response(
            status_code=200,
            headers={"Content-Type": "text/css"},
            body=open(f"static/{request.path_params.get('file')}", "r").read(),
        )

    async def index(self, _: Request) -> Response:
        template = self.env.get_template("index.html")
        return Response(
            status_code=200,
            headers={"Content-Type": "text/html"},
            body=template.render(content=self.content, page_content=self.content),
        )

    async def content_handler(self, request: Request) -> Response:
        # honestly.
        # idk why i did this
        # but im not changing it
        for category in self.content:
            if category.name == request.path_params.get("category"):
                for post in category.posts:
                    if post.id == int(request.path_params.get("post_id")):
                        return Response(
                            status_code=200,
                            headers={"Content-Type": "text/html"},
                            body=post.content,
                        )
        return Response(
            status_code=200,
            headers={"Content-Type": "text/html"},
            body="erm",
        )


if __name__ == "__main__":
    raise SystemExit(Server().start(port=8081) or 0)
