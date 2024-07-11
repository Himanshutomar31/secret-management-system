import streamlit as st
import requests

st.set_page_config(page_title="Secret Management System", layout="wide")

BASE_URL = ""  
MODE = "demo"  

if "projects" not in st.session_state:
    st.session_state.projects = [
        {"id": 1, "name": "Project Alpha"},
        {"id": 2, "name": "Project Beta"}
    ]
if "secrets" not in st.session_state:
    st.session_state.secrets = {
        1: [
            {"id": 1, "name": "API_KEY", "value": "abc123"},
            {"id": 2, "name": "DB_PASSWORD", "value": "pass@123"}
        ],
        2: [
            {"id": 1, "name": "API_SECRET", "value": "xyz789"},
            {"id": 2, "name": "SERVICE_ACCOUNT", "value": "service@123"}
        ]
    }

# Function to simulate authentication
def authenticate(username, password):
    if username == "admin" and password == "admin":
        return {"token": "dummy_token"}
    return None

# Register API call
def register_user(username, email, password):
    if MODE == "demo":
        return {"status_code": 201}
    response = requests.post(f"{BASE_URL}/register", json={
        "username": username,
        "email": email,
        "password": password
    })
    return response

# Login API call
def login_user(username, password):
    if MODE == "demo":
        return {"status_code": 200, "token": "dummy_token"}
    response = requests.post(f"{BASE_URL}/login", json={
        "username": username,
        "password": password
    })
    return response

# Create project API call
def create_project_api(project_name):
    if MODE == "demo":
        new_id = max([p["id"] for p in st.session_state.projects]) + 1
        st.session_state.projects.append({"id": new_id, "name": project_name})
        st.session_state.secrets[new_id] = []
        return {"status_code": 201}
    response = requests.post(f"{BASE_URL}/projects", json={"name": project_name}, headers={
        "Authorization": f"Bearer {st.session_state['token']}"})
    return response

# Add secret API call
def add_secret_api(project_id, secret_name, secret_value):
    if MODE == "demo":
        new_id = len(st.session_state.secrets[project_id]) + 1
        st.session_state.secrets[project_id].append({"id": new_id, "name": secret_name, "value": secret_value})
        return {"status_code": 201}
    response = requests.post(f"{BASE_URL}/projects/{project_id}/secrets", json={
        "name": secret_name,
        "value": secret_value
    }, headers={"Authorization": f"Bearer {st.session_state['token']}"})
    return response

# Rotate secret API call
def rotate_project_secret_api(project_id):
    if MODE == "demo":
        return {"status_code": 200}
    response = requests.post(f"{BASE_URL}/projects/{project_id}/rotate", headers={
        "Authorization": f"Bearer {st.session_state['token']}"})
    return response

# Retrieve secrets API call
def retrieve_secrets_api(project_id):
    if MODE == "demo":
        return {"status_code": 200, "secrets": st.session_state.secrets[project_id]}
    response = requests.get(f"{BASE_URL}/projects/{project_id}/secrets", headers={
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
            st.session_state["logged_in"] = True
            st.experimental_rerun()
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
    for project in st.session_state.projects:
        with st.expander(project["name"]):
            st.subheader("Secrets")
            secrets_response = retrieve_secrets_api(project["id"])
            if secrets_response["status_code"] == 200:
                secrets = secrets_response["secrets"]
                for secret in secrets:
                    st.write(f"Name: {secret['name']}, Value: {secret['value']}")

            st.button("Add Secret", key=f"add_secret_{project['id']}", on_click=add_secret, args=(project["id"],))
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

# Add secret function (dummy implementation)
def add_secret(project_id):
    st.session_state["current_project_id"] = project_id
    st.session_state["adding_secret"] = True
    st.experimental_rerun()

# Rotate project secret function
def rotate_project_secret(project_id):
    response = rotate_project_secret_api(project_id)
    if response["status_code"] == 200:
        st.success(f"Secrets for project {project_id} rotated successfully!")
    else:
        st.error("Failed to rotate secrets")

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
                st.experimental_rerun()
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
