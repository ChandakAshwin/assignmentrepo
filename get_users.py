import json
from db import get_db_connection

def lambda_handler(event, context):
    body = json.loads(event['body'])
    user_id = body.get('user_id')
    mob_num = body.get('mob_num')
    manager_id = body.get('manager_id')

    conn = get_db_connection()

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            if user_id:
                cursor.execute("SELECT * FROM users WHERE user_id = %s AND is_active = TRUE", (user_id,))
            elif mob_num:
                cursor.execute("SELECT * FROM users WHERE mob_num = %s AND is_active = TRUE", (mob_num,))
            elif manager_id:
                cursor.execute("SELECT * FROM users WHERE manager_id = %s AND is_active = TRUE", (manager_id,))
            else:
                cursor.execute("SELECT * FROM users WHERE is_active = TRUE")

            users = cursor.fetchall()
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
    finally:
        conn.close()

    return {"statusCode": 200, "body": json.dumps({"users": users})}
