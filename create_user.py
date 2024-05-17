import json
import uuid
import re
import psycopg2
from datetime import datetime
from db import get_db_connection

def validate_full_name(full_name):
    return bool(full_name)

def validate_mob_num(mob_num):
    mob_num = re.sub(r'[^0-9]', '', mob_num)
    if len(mob_num) == 10:
        return mob_num
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
    full_name = body.get('full_name')
    mob_num = body.get('mob_num')
    pan_num = body.get('pan_num')
    manager_id = body.get('manager_id')

    if not validate_full_name(full_name):
        return {"statusCode": 400, "body": json.dumps({"error": "Invalid full_name"})}

    mob_num = validate_mob_num(mob_num)
    if not mob_num:
        return {"statusCode": 400, "body": json.dumps({"error": "Invalid mob_num"})}

    pan_num = validate_pan_num(pan_num)
    if not pan_num:
            return {"statusCode": 400, "body": json.dumps({"error": "Invalid pan_num"})}

    conn = get_db_connection()

    if manager_id and not validate_manager_id(manager_id, conn):
        return {"statusCode": 400, "body": json.dumps({"error": "Invalid manager_id"})}

    user_id = str(uuid.uuid4())
    created_at = datetime.now()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (user_id, full_name, mob_num, pan_num, manager_id, created_at, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (user_id, full_name, mob_num, pan_num, manager_id, created_at, True)
            )
            conn.commit()
    except Exception as e:
        conn.rollback()
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
    finally:
        conn.close()

    return {"statusCode": 200, "body": json.dumps({"message": "User created successfully"})}
