import json
import uuid
import re
from datetime import datetime
from db import get_db_connection

def validate_full_name(full_name):
    return bool(full_name)

def validate_mob_num(mob_num):
    mob_num = re.sub(r'[^0-9]', '', mob_num)
    if len(mob_num) == 10:
        return     mob_num
    elif len(mob_num) == 11 and mob_num.startswith('0'):
        return mob_num[1:]
    elif len(mob_num) == 12 and mob_num.startswith('91'):
        return mob_num[2:]
    else:
        return None

def validate_pan_num(pan_num):
    pattern = re.compile(r'^[A-Z]{5}[0-9]{4}[A-Z]$')
    pan_num = pan_num.upper()
    return pan_num if pattern.match(pan_num) else None

def validate_manager_id(manager_id, conn):
    with conn.cursor() as cursor:
        cursor.execute("SELECT manager_id FROM managers WHERE manager_id = %s", (manager_id,))
        return cursor.fetchone() is not None

def lambda_handler(event, context):
    body = json.loads(event['body'])
    user_ids = body.get('user_ids')
    update_data = body.get('update_data')

    if not user_ids or not isinstance(user_ids, list):
        return {"statusCode": 400, "body": json.dumps({"error": "user_ids must be a list of UUIDs"})}

    if not update_data or not isinstance(update_data, dict):
        return {"statusCode": 400, "body": json.dumps({"error": "update_data must be a dictionary"})}

    conn = get_db_connection()
    cursor = conn.cursor()

    valid_updates = ['full_name', 'mob_num', 'pan_num', 'manager_id']
    if any(key not in valid_updates for key in update_data.keys()):
        return {"statusCode": 400, "body": json.dumps({"error": "Invalid update keys"})}

    if len(update_data.keys()) > 1 and 'manager_id' in update_data:
        return {"statusCode": 400, "body": json.dumps({"error": "Only manager_id can be updated in bulk"})}

    try:
        for user_id in user_ids:
            cursor.execute("SELECT * FROM users WHERE user_id = %s AND is_active = TRUE", (user_id,))
            if cursor.fetchone() is None:
                return {"statusCode": 404, "body": json.dumps({"error": f"User with id {user_id} not found"})}

        for user_id in user_ids:
            if 'full_name' in update_data:
                if not validate_full_name(update_data['full_name']):
                    return {"statusCode": 400, "body": json.dumps({"error": "Invalid full_name"})}
                cursor.execute("UPDATE users SET full_name = %s, updated_at = %s WHERE user_id = %s", 
                               (update_data['full_name'], datetime.now(), user_id))

            if 'mob_num' in update_data:
                mob_num = validate_mob_num(update_data['mob_num'])
                if not mob_num:
                    return {"statusCode": 400, "body": json.dumps({"error": "Invalid mob_num"})}
                cursor.execute("UPDATE users SET mob_num = %s, updated_at = %s WHERE user_id = %s", 
                               (mob_num, datetime.now(), user_id))

            if 'pan_num' in update_data:
                pan_num = validate_pan_num(update_data['pan_num'])
                if not pan_num:
                    return {"statusCode": 400, "body": json.dumps({"error": "Invalid pan_num"})}
                cursor.execute("UPDATE users SET pan_num = %s, updated_at = %s WHERE user_id = %s", 
                               (pan_num, datetime.now(), user_id))

            if 'manager_id' in update_data:
                if not validate_manager_id(update_data['manager_id'], conn):
                    return {"statusCode": 400, "body": json.dumps({"error": "Invalid manager_id"})}
                
                cursor.execute("SELECT manager_id FROM users WHERE user_id = %s", (user_id,))
                current_manager_id = cursor.fetchone()[0]
                
                if current_manager_id != update_data['manager_id']:
                    cursor.execute("UPDATE users SET is_active = FALSE WHERE user_id = %s", (user_id,))
                    cursor.execute(
                        """
                        INSERT INTO users (user_id, full_name, mob_num, pan_num, manager_id, created_at, updated_at, is_active)
                        SELECT user_id, full_name, mob_num, pan_num, %s, created_at, %s, TRUE
                        FROM users WHERE user_id = %s
                        """,
                        (update_data['manager_id'], datetime.now(), user_id)
                    )

        conn.commit()
    except Exception as e:
        conn.rollback()
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
    finally:
        conn.close()

    return {"statusCode": 200, "body": json.dumps({"message": "User(s) updated successfully"})}

