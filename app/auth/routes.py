from . import auth


@auth.route("/test")
def test():
    return "Auth blueprint is working!"