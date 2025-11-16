import os
from flask import Flask, render_template
from supabase import create_client


SUPABASE_URL = "https://csgiuqsmzaohurfstbtj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNzZ2l1cXNtemFvaHVyZnN0YnRqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE5NDExODksImV4cCI6MjA3NzUxNzE4OX0.cHDdBRJUEDkFWehhFoukwe0tpmhuOf_DpXPWrRcVTPc"


supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask("bulochka_pribulochka")


@app.route("/")
def index():
    # Загружаем всех пользователей
    res = supabase.table("users").select("*").execute()
    users = res.data or []

    # Группируем по group_name
    groups = {}
    for u in users:
        g = u.get("group_name", "Unknown")
        groups.setdefault(g, []).append(u)

    # Сортируем группы и имена
    for g in groups:
        groups[g] = sorted(groups[g], key=lambda x: (x["surname"], x["name"]))
    sorted_groups = dict(sorted(groups.items()))

    return render_template("index.html", groups=sorted_groups)


@app.route("/group/<group_name>")
def group_view(group_name):
    res = supabase.table("users").select("*").eq("group_name", group_name).execute()
    students = sorted(res.data or [], key=lambda x: (x["surname"], x["name"]))
    return render_template("group.html", group=group_name, students=students)


@app.route("/student/<int:user_id>")
def student_view(user_id):
    # Получаем информацию о пользователе
    res_user = supabase.table("users").select("*").eq("user_id", user_id).execute()
    user = res_user.data[0] if res_user.data else None

    # Получаем все ответы студента
    res_quiz = (
        supabase.table("quizzes")
        .select("*")
        .eq("user_id", user_id)
        .order("timestamp", desc=False)
        .execute()
    )
    quizzes = res_quiz.data or []

    # Группируем по названию квиза (name)
    grouped = {}
    for q in quizzes:
        quiz_name = q.get("name", "Без названия")
        grouped.setdefault(quiz_name, []).append(q)

    return render_template("student.html", user=user, quizzes_grouped=grouped)




if __name__ == "__main__":
    app.run(port=7387, debug=True)
