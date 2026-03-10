# crud/__init__.py — expõe as funções CRUD para importação direta
from .users import (
    get_user, get_user_by_email, get_user_by_username,
    get_users, create_user, update_user, delete_user,
)
from .posts import (
    get_post, get_post_by_slug, get_posts,
    create_post, update_post, delete_post,
)
