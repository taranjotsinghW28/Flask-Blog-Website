from flask import render_template, request, redirect, url_for, flash, Blueprint, session, jsonify
from app.models import User, Post, Comment, db
from sqlalchemy.sql.expression import func
from sqlalchemy import select
from flask_login import login_required, current_user
from app.models import Post, User, Like, Message
from datetime import datetime

# Blueprint
post_bp = Blueprint("post", __name__)

# Home / Feed
@post_bp.route("/")
def view_blog():
    if "user_id" not in session:
        flash("Login First")
        return redirect(url_for("auth.login"))

    total_posts = db.session.scalar(select(func.count()).select_from(Post))
    limit_count = min(10, total_posts)
    random_posts = Post.query.order_by(func.random()).limit(limit_count).all()

    return render_template("feed.html", posts=random_posts, current_page="feed")

# User's own blogs
@post_bp.route("/yourfeed")
def view_yourblog():
    if "user_id" not in session:
        flash("Login First")
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]
    tasks = Post.query.filter_by(user_id=user_id).all()
    return render_template("yoursblog.html", tasks=tasks, current_page="profile")

# Add new blog
@post_bp.route("/addblog", methods=["GET", "POST"])
def add_blog():
    if "user_id" not in session:
        flash("Login First")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        user_id = session["user_id"]

        new_blog = Post(title=title, content=content, user_id=user_id)
        db.session.add(new_blog)
        db.session.commit()

        flash("Blog created successfully!")
        return redirect(url_for("post.view_yourblog"))

    return render_template("addblog.html", current_page="addblog")

# Delete blog
@post_bp.route("/delete/<int:task_id>")
def delete_blog(task_id):
    if "user_id" not in session:
        flash("Please login first")
        return redirect(url_for("auth.login"))

    task = Post.query.get_or_404(task_id)
    if task.user_id != session["user_id"]:
        flash("You cannot delete someone else's blog!")
        return redirect(url_for("post.view_blog"))

    db.session.delete(task)
    db.session.commit()
    flash("Blog deleted successfully!")
    return redirect(url_for("post.view_blog"))

# Edit blog
@post_bp.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit_blog(task_id):
    if "user_id" not in session:
        flash("Please login first")
        return redirect(url_for("auth.login"))

    task = Post.query.get_or_404(task_id)
    if task.user_id != session["user_id"]:
        flash("You cannot edit this blog!")
        return redirect(url_for("post.view_blog"))

    if request.method == "POST":
        task.title = request.form.get("title")
        task.content = request.form.get("content")
        db.session.commit()
        flash("Blog updated successfully!")
        return redirect(url_for("post.view_yourblog"))

    return render_template("edit_blog.html", task=task, current_page="edit")

# Messages page (placeholder)
@post_bp.route("/messages")
def messages_page():
    if "user_id" not in session:
        flash("Login First")
        return redirect(url_for("auth.login"))

    return render_template("messages.html", current_page="messages")


# ✅ Add Comment / Reply
@post_bp.route("/add_comment/<int:post_id>", methods=["POST"])
@login_required
def add_comment(post_id):
    """Handles submission of a new comment or reply for a blog post."""

    comment_content = request.form.get("comment_content")
    parent_id = request.form.get("parent_id")  # Get parent_id from hidden input

    if not comment_content:
        flash("Comment cannot be empty.")
        return redirect(url_for("post.view_blog"))

    # Convert parent_id to integer if it exists
    if parent_id:
        parent_id = int(parent_id)
    else:
        parent_id = None

    # Create a new Comment object
    new_comment = Comment(
        content=comment_content,
        user_id=current_user.id,
        post_id=post_id,
        parent_id=parent_id  # Assign parent_id for replies
    )

    # Save to database
    db.session.add(new_comment)
    db.session.commit()

    flash("Your comment has been posted successfully!")
    return redirect(url_for("post.view_blog"))


# ----------------------------
# Chats list route
# ----------------------------
@post_bp.route("/chats")
def chat_list():
    if "user_id" not in session:
        flash("Login first to view chats.", "error")
        return redirect(url_for("auth.login"))
    
    current_user_id = session["user_id"]
    
    # Get all unique user IDs who have chatted with current user
    sent = db.session.query(Message.receiver_id.label("user_id")).filter_by(sender_id=current_user_id)
    received = db.session.query(Message.sender_id.label("user_id")).filter_by(receiver_id=current_user_id)
    
    chat_user_ids = {row.user_id for row in sent.union(received)}
    chat_users = User.query.filter(User.id.in_(chat_user_ids)).all()
    
    # Prepare chats with last message
    chats = []
    for user in chat_users:
        last_msg = Message.query.filter(
            ((Message.sender_id == current_user_id) & (Message.receiver_id == user.id)) |
            ((Message.sender_id == user.id) & (Message.receiver_id == current_user_id))
        ).order_by(Message.date_sent.desc()).first()
        chats.append({
            "other_user": user,
            "last_message": last_msg
        })
    
    return render_template("messages.html", chats=chats, current_page="messages")

# ----------------------------
# Particular user chat route
# ----------------------------
@post_bp.route("/chat/<int:other_user_id>", methods=["GET", "POST"])
def chat_with_user(other_user_id):
    if "user_id" not in session:
        flash("Login first to chat.", "error")
        return redirect(url_for("auth.login"))
    
    current_user_id = session["user_id"]
    other_user = User.query.get_or_404(other_user_id)
    
    if request.method == "POST":
        content = request.form.get("message_content")
        if content:
            message = Message(
                sender_id=current_user_id,
                receiver_id=other_user_id,
                content=content,
                date_sent=datetime.utcnow()  # make sure timestamp is set
            )
            db.session.add(message)
            db.session.commit()
            return redirect(url_for("post.chat_with_user", other_user_id=other_user_id))
    
    # Fetch all chat messages with this user
    messages = Message.query.filter(
        ((Message.sender_id == current_user_id) & (Message.receiver_id == other_user_id)) |
        ((Message.sender_id == other_user_id) & (Message.receiver_id == current_user_id))
    ).order_by(Message.date_sent.asc()).all()
    
    return render_template(
        "particular_messages.html",
        other_user=other_user,
        messages=messages,
        current_page="messages"  # ensures header highlights Messages
    )


# ----------------------------
# Like/Unlike Post Route - MODIFIED FOR AJAX 
# ----------------------------
@post_bp.route("/like/<int:post_id>", methods=["POST"])
def like_post(post_id):
    if "user_id" not in session:
        # For AJAX, return a 401 error code instead of redirecting
        return jsonify({"success": False, "error": "Login required"}), 401 

    user_id = session["user_id"]
    post = Post.query.get_or_404(post_id)

    # Check if the user has already liked the post
    existing_like = Like.query.filter_by(user_id=user_id, post_id=post_id).first()

    if existing_like:
        db.session.delete(existing_like)
        db.session.commit()
    else:
        new_like = Like(user_id=user_id, post_id=post_id)
        db.session.add(new_like)
        db.session.commit()
    
    # Returns the new count and status as JSON
    return jsonify({
        "success": True, 
        "likes": len(post.likes),
        "liked": not existing_like 
    })