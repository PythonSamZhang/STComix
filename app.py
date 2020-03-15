from stcomix import create_app
from stcomix.models import User, Role, Post, Book, Dashboard, Comment

app = create_app()


@app.shell_context_processor
def context_processor():
    return dict(User=User, Role=Role, Post=Post, Book=Book, Dashboard=Dashboard, Comment=Comment)


@app.cli.command()
def deploy():
    """Deploy the website"""
    Role.insert_roles()
    User.create_admin()
    Dashboard.insert_dashboard()


if __name__ == '__main__':
    app.run()
