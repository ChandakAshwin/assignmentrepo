import json
from db import get_db_connection

def lambda_handler(event, context):
    body = json.loads(event['body'])
    user_id = body.get('user_id')
    mob_num = body.get('mob_num')

    conn = get_db_connection()

    try:
        with conn.cursor() as cursor:
            if user_id:
                cursor.execute("SELECT user_id FROM users WHERE user_id = %s AND is_active = TRUE", (user_id,))
            elif mob_num:
                cursor.execute("SELECT user_id FROM users WHERE mob_num = %s AND is_active = TRUE", (mob_num,))
            else:
                return {"statusCode": 400, "body": json.dumps({"error": "user_id or mob_num required"})}

            if cursor.fetchone() is None:
                return {"statusCode": 404, "body": json.dumps({"error": "User not found"})}

            cursor.execute("DELETE FROM users WHERE user_id = %s OR mob_num = %s", (user_id, mob_num))
            conn.commit()
    except Exception as e:
        conn.rollback()
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
    finally:
        conn.close()

    return {"statusCode": 200, "body": json.dumps({"message": "User deleted successfully"})}
