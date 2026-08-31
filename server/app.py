from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, Article, User, ArticleSchema, UserSchema

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = b'super-secret-key-change-in-production'   # required for sessions

# Initialize extensions (no CORS – React proxy handles cross-origin)
db.init_app(app)
migrate = Migrate(app, db)

# Create schema instances
article_schema = ArticleSchema()
articles_schema = ArticleSchema(many=True)
user_schema = UserSchema()
users_schema = UserSchema(many=True)

# ----- ROUTES -----

# Root route (optional)
@app.route('/')
def index():
    return jsonify({"message": "Welcome to the Blog API"})

# List all articles (optional)
@app.route('/articles', methods=['GET'])
def get_articles():
    articles = Article.query.all()
    return jsonify(articles_schema.dump(articles))

# Single article with session paywall
@app.route('/articles/<int:id>', methods=['GET'])
def get_article(id):
    # Use db.session.get() to avoid legacy warning
    article = db.session.get(Article, id)

    if not article:
        return jsonify({"error": "Article not found"}), 404

    # Initialize session counter if not present
    if 'page_views' not in session:
        session['page_views'] = 0

    # Increment page views
    session['page_views'] += 1

    # Check limit
    if session['page_views'] <= 3:
        # Correct serialisation: dump + jsonify
        return jsonify(article_schema.dump(article)), 200
    else:
        return jsonify({"message": "Maximum pageview limit reached"}), 401

# Clear session (for testing)
@app.route('/clear', methods=['GET'])
def clear_session():
    session.clear()
    return jsonify({"message": "Session cleared"}), 200

# ----- RUN -----
if __name__ == '__main__':
    app.run(port=5555, debug=True)