web: gunicorn perks:app --timeout 15 --keep-alive 5 --log-level debug
upgrade:  python db_tasks.py db upgrade head 
add_admin: python db_tasks.py create_admin zematynnad+admin@gmail.com
