from src.database.config import supabase
import bcrypt

def check_teacher_exists(username):
    response = supabase.table("teachers").select("*").eq("username", username).execute()
    return len(response.data) > 0 # Returns True if teacher exists, False otherwise

def create_teacher(username, password, name):
    data ={
        "username": username,
        "password": bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
        "name": name
    }
    response = supabase.table("teachers").insert(data).execute()
    return response.data[0] if response.data else None

def teacher_login(username, password):
    response = supabase.table("teachers").select("*").eq("username", username).execute()
    if len(response.data) == 0:
        return None  # Teacher not found
    teacher = response.data[0]
    if bcrypt.checkpw(password.encode('utf-8'), teacher['password'].encode('utf-8')):
        return teacher  # Successful login
    else:
        return None  # Incorrect password

def get_all_students():
    response = supabase.table("students").select("*").execute()
    return response.data if response.data else []