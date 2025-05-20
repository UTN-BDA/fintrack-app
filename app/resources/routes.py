class RouteApp:
    def init_app(self, app):
        from app.resources import user_bp, category_bp, transaction_bp
        app.register_blueprint(user_bp, url_prefix='/users')
        app.register_blueprint(category_bp, url_prefix='/categories')
        app.register_blueprint(transaction_bp, url_prefix='/transactions')
