import streamlit as st
import csv
import json
import os

# Streamlit configurations
st.set_page_config(page_title="Secret Management System", layout="wide")

BASE_URL = "http://localhost:9000"
MODE = "demo"  # demo

# Files for storing data
USER_FILE = "users.csv"
PROJECT_FILE = "projects.json"
SECRET_FILE = "secrets.json"

# Initialize the user file with an admin user if it doesn't exist
def init_user_file():
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["username", "email", "password", "role"])
            writer.writerow(["admin", "admin@example.com", "admin", "admin"])

# Initialize the projects file if it doesn't exist
def init_project_file():
    if not os.path.exists(PROJECT_FILE):
        with open(PROJECT_FILE, mode='w') as file:
            json.dump([
                {"id": 1, "name": "Project Alpha", "user": "admin"},
                {"id": 2, "name": "Project Beta", "user": "admin"}
            ], file)

# Initialize the secrets file if it doesn't exist
def init_secret_file():
    if not os.path.exists(SECRET_FILE):
        with open(SECRET_FILE, mode='w') as file:
            json.dump({
                "1": [
                    {"id": 1, "name": "API_KEY", "value": "abc123"},
                    {"id": 2, "name": "DB_PASSWORD", "value": "pass@123"}
                ],
                "2": [
                    {"id": 1, "name": "API_SECRET", "value": "xyz789"},
                    {"id": 2, "name": "SERVICE_ACCOUNT", "value": "service@123"}
                ]
            }, file)

init_user_file()
init_project_file()
init_secret_file()

# Function to read users from the CSV file
def read_users():
    users = []
    with open(USER_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            users.append(row)
    return users

# Function to read projects from the JSON file
def read_projects():
    with open(PROJECT_FILE, mode='r') as file:
        projects = json.load(file)
    return projects

# Function to read secrets from the JSON file
def read_secrets():
    with open(SECRET_FILE, mode='r') as file:
        secrets = json.load(file)
    return secrets

# Function to write projects to the JSON file
def write_projects(projects):
    with open(PROJECT_FILE, mode='w') as file:
        json.dump(projects, file)

# Function to write secrets to the JSON file
def write_secrets(secrets):
    with open(SECRET_FILE, mode='w') as file:
        json.dump(secrets, file)

# Function to authenticate user from the CSV file
def authenticate(username, password):
    users = read_users()
    for user in users:
        if user["username"] == username and user["password"] == password:
            return {"token": "dummy_token", "role": user["role"]}
    return None

# Register a new user in the CSV file
def register_user(username, email, password):
    if MODE == "demo":
        with open(USER_FILE, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([username, email, password, "user"])
        return {"status_code": 201}
    response = requests.post(f"{BASE_URL}/api/register", json={
        "username": username,
        "email": email,
        "password": password
    })
    return response

# Login API call
def login_user(username, password):
    if MODE == "demo":
        auth_response = authenticate(username, password)
        if auth_response:
            return {"status_code": 200, "token": auth_response["token"], "role": auth_response["role"]}
        return {"status_code": 401}
    response = requests.post(f"{BASE_URL}/api/login", json={
        "username": username,
        "password": password
    })
    return response

# Create project API call
def create_project_api(project_name):
    if MODE == "demo":
        projects = read_projects()
        new_id = max([p["id"] for p in projects], default=0) + 1
        projects.append({"id": new_id, "name": project_name, "user": "admin"})
        write_projects(projects)
        
        secrets = read_secrets()
        secrets[new_id] = []
        write_secrets(secrets)
        
        return {"status_code": 201}
    response = requests.post(f"{BASE_URL}/api/projects", json={"name": project_name}, headers={
        "Authorization": f"Bearer {st.session_state['token']}"})
    return response

# Add secret API call
def add_secret_api(project_id, secret_name, secret_value):
    if MODE == "demo":
        secrets = read_secrets()
        new_id = len(secrets.get(str(project_id), [])) + 1
        secrets[str(project_id)].append({"id": new_id, "name": secret_name, "value": secret_value})
        write_secrets(secrets)
        return {"status_code": 201}
    response = requests.post(f"{BASE_URL}/api/projects/{project_id}/secrets", json={
        "name": secret_name,
        "value": secret_value
    }, headers={"Authorization": f"Bearer {st.session_state['token']}"})
    return response

# Delete secret API call
def delete_secret_api(project_id, secret_id):
    if MODE == "demo":
        secrets = read_secrets()
        secrets[str(project_id)] = [secret for secret in secrets.get(str(project_id), []) if secret["id"] != secret_id]
        write_secrets(secrets)
        return {"status_code": 200}
    response = requests.delete(f"{BASE_URL}/api/projects/{project_id}/secrets/{secret_id}", headers={
        "Authorization": f"Bearer {st.session_state['token']}"})
    return response

# Rotate secret API call
def rotate_project_secret_api(project_id):
    if MODE == "demo":
        return {"status_code": 200}
    response = requests.post(f"{BASE_URL}/api/projects/{project_id}/rotate", headers={
        "Authorization": f"Bearer {st.session_state['token']}"})
    return response

# Retrieve secrets API call
def retrieve_secrets_api(project_id):
    if MODE == "demo":
        secrets = read_secrets()
        return {"status_code": 200, "secrets": secrets.get(str(project_id), [])}
    response = requests.get(f"{BASE_URL}/api/projects/{project_id}/secrets", headers={
        "Authorization": f"Bearer {st.session_state['token']}"})
    return response

# Login page
def login():
    st.title("Secret Management System - Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        auth_response = login_user(username, password)
        if auth_response["status_code"] == 200:
            st.session_state["token"] = auth_response.get("token", "dummy_token")
            st.session_state["role"] = auth_response.get("role", "user")
            st.session_state["logged_in"] = True
            st.rerun()
        else:
            st.error("Invalid username or password")

# Main application layout
def main_app():
    st.title("Secret Management System")
    st.sidebar.title("Menu")
    menu = st.sidebar.radio("Navigate", ["Projects", "Create Project"])

    if menu == "Projects":
        view_projects()
    elif menu == "Create Project":
        create_project()

# View projects and secrets
def view_projects():
    st.subheader("Projects")
    projects = read_projects()
    for project in projects:
        with st.expander(project["name"]):
            st.subheader("Secrets")
            secrets_response = retrieve_secrets_api(project["id"])
            if secrets_response["status_code"] == 200:
                secrets = secrets_response["secrets"]
                for secret in secrets:
                    st.write(f"Name: {secret['name']}, Value: {secret['value']}")
                    if st.button("Delete Secret", key=f"delete_secret_{project['id']}_{secret['id']}"):
                        delete_secret(project["id"], secret["id"])

            if st.button("Add Secret", key=f"add_secret_{project['id']}"):
                st.session_state["current_project_id"] = project["id"]
                st.session_state["adding_secret"] = True
                st.rerun()
            st.button("Rotate Secrets", key=f"rotate_secret_{project['id']}", on_click=rotate_project_secret, args=(project["id"],))

# Create project page
def create_project():
    st.subheader("Create Project")
    project_name = st.text_input("Project Name")
    if st.button("Create"):
        response = create_project_api(project_name)
        if response["status_code"] == 201:
            st.success(f"Project '{project_name}' created successfully!")
        else:
            st.error("Failed to create project")

# Add secret function
def add_secret(project_id):
    st.session_state["current_project_id"] = project_id
    st.session_state["adding_secret"] = True
    st.rerun()

# Rotate project secret function
def rotate_project_secret(project_id):
    response = rotate_project_secret_api(project_id)
    if response["status_code"] == 200:
        st.success(f"Secrets for project {project_id} rotated successfully!")
    else:
        st.error("Failed to rotate secrets")

# Delete secret function
def delete_secret(project_id, secret_id):
    response = delete_secret_api(project_id, secret_id)
    if response["status_code"] == 200:
        st.success(f"Secret {secret_id} deleted successfully from project {project_id}!")
        st.rerun()
    else:
        st.error("Failed to delete secret")

# Handle adding secrets
def handle_add_secret():
    st.subheader("Add Secret")
    project_id = st.session_state.get("current_project_id")
    if project_id:
        secret_name = st.text_input("Secret Name")
        secret_value = st.text_input("Secret Value")
        if st.button("Add"):
            response = add_secret_api(project_id, secret_name, secret_value)
            if response["status_code"] == 201:
                st.success(f"Secret '{secret_name}' added successfully to project {project_id}!")
                st.session_state["adding_secret"] = False
                st.rerun()
            else:
                st.error("Failed to add secret")

# Main application logic
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "adding_secret" in st.session_state and st.session_state["adding_secret"]:
    handle_add_secret()
elif st.session_state["logged_in"]:
    main_app()
else:
    login()
