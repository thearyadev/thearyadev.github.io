import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable

import frontmatter  # type: ignore
import mistune
from jinja2 import Environment, FileSystemLoader
from robyn import Request, Response, Robyn


@dataclass
class Post:
    id: int
    title: str
    date: str
    description: str
    content: str


@dataclass
class Category:
    name: str
    posts: list[Post]


def get_content() -> list[Category]:
    content_root = Path("pages").resolve()
    content: list[Category] = []

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
                                description=post_content["description"],
                                content=mistune.html(post_content.content),
                            )
                        )
            content.append(
                Category(
                    name=category.name,
                    posts=sorted(
                        posts, key=lambda x: datetime.strptime(x.date, "%Y-%m-%d")
                    ),
                )
            )

    return content


class Server(Robyn):
    def __init__(self) -> None:
        super().__init__(__file__)
        self.get("/")(self.index)
        self.get("/:category/:post_id")(self.content_handler)
        self.get("/:category")(self.category_handler)

        self.add_directory("/static", "public")
        self.content: list[Category] = get_content()
        self.env = Environment(loader=FileSystemLoader("templates"))

    async def index(self, _: Request) -> Response:
        template = self.env.get_template("index.html")
        return Response(
            status_code=200,
            headers={"Content-Type": "text/html"},
            body=template.render(content=self.content, page_content=self.content),
        )

    async def category_handler(self, request: Request) -> Response:
        for category in self.content:
            if category.name == request.path_params.get("category"):
                template = self.env.get_template("category.html")
                return Response(
                    status_code=200,
                    headers={"Content-Type": "text/html"},
                    body=template.render(content=self.content, category=category),
                )
        return Response(
            status_code=200,
            headers={"Content-Type": "text/html"},
            body="erm",
        )

    async def content_handler(self, request: Request) -> Response:
        # honestly.
        # idk why i did this
        # but im not changing it
        template = self.env.get_template("post.html")
        for category in self.content:
            if category.name == request.path_params.get("category"):
                for post in category.posts:
                    if post.id == int(request.path_params.get("post_id") or -1):
                        return Response(
                            status_code=200,
                            headers={"Content-Type": "text/html"},
                            body=template.render(content=self.content, post=post),
                        )
        return Response(
            status_code=200,
            headers={"Content-Type": "text/html"},
            body="erm",
        )


if __name__ == "__main__":
    raise SystemExit(Server().start(port=8081, url="0.0.0.0") or 0)
