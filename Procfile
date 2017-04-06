web: gunicorn perks:app --timeout 15 --keep-alive 5 --log-level debug
init:  python db_tasks.py upgrade head 
upgrade:  python db_tasks.py upgrade head 
