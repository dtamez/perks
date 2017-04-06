web: gunicorn perks:app --timeout 15 --keep-alive 5 --log-level debug
init:  python db_tasks.py db upgrade head 
init: python db_tasks.py create_admin zematynnad+admin@gmail.com
upgrade:  python db_tasks.py db upgrade head 
