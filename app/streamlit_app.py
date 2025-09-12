import streamlit as st
import requests
import os

# Default for local dev, overridden in Docker
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")


st.set_page_config(page_title="To-Do App", page_icon="📝", layout="centered")

# -------------------- Auth + Session Handling --------------------
if "user_email" not in st.session_state:  # User not logged in yet
    choice = st.sidebar.selectbox("Menu", ["Login", "Register"])

    if choice == "Register":
        st.title("📝 To-Do App - Register")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Register"):
            if not email or not password:
                st.error("Email and password required")
            else:
                res = requests.post(f"{API_URL}/register", json={"email": email, "password": password})
                if res.status_code == 200:
                    st.success("User registered! You can login now.")
                else:
                    st.error(res.json().get("detail", "Registration failed"))

    elif choice == "Login":
        st.title("📝 To-Do App - Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if not email or not password:
                st.error("Email and password required")
            else:
                res = requests.post(f"{API_URL}/login", json={"email": email, "password": password})
                if res.status_code == 200:
                    st.session_state["user_email"] = email
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error(res.json().get("detail", "Login failed"))

else:  # -------------------- Todos Page --------------------
    user_email = st.session_state["user_email"]

    # Sidebar only shows Logout now
    if st.sidebar.button("Logout"):
        st.session_state.pop("user_email")
        st.success("Logged out successfully")
        st.rerun()

    st.title("Plan your day!")
    st.markdown(f"👋 Hi, **{user_email}**")

    # Add Task
    st.subheader("Add a Task")
    new_title = st.text_input("Enter task title")
    new_desc = st.text_area("Enter description (optional)")

    if st.button("Add Task"):
        if not new_title.strip():
            st.warning("Task cannot be empty!")
        else:
            data = {"title": new_title, "description": new_desc}
            res = requests.post(f"{API_URL}/todos/", params={"user_email": user_email}, json=data)
            if res.status_code == 200:
                st.success("Task added!")
                st.rerun()
            else:
                st.error(res.json().get("detail", "Failed to add task"))

    # Show Tasks
    st.subheader("Your Tasks")
    response = requests.get(f"{API_URL}/todos/", params={"user_email": user_email})

    if response.status_code == 200:
        tasks = response.json()
        if tasks:
            for task in tasks:
                col1, col2, col3, col4 = st.columns([5, 2, 2, 2])

                # Display task
                if task.get("status") == "Complete":
                    col1.markdown(f"✅ **Completed:** {task['title']}")
                else:
                    col1.markdown(f"🕘 **Due:** {task['title']}")

                # Done button
                if task.get("status") == "Incomplete":
                    if col2.button("✅ Done", key=f"done_{task['_id']}"):
                        update_data = {
                            "task_id": task["_id"],
                            "title": task["title"],
                            "description": task.get("description", ""),
                            "status": "Complete"
                        }
                        res = requests.put(f"{API_URL}/todos/", params={"user_email": user_email}, json=update_data)
                        if res.status_code == 200:
                            st.rerun()

                # Update button
                if col3.button("✏️ Update", key=f"upd_{task['_id']}"):
                    with st.expander(f"Update Task: {task['title']}", expanded=True):
                        new_title = st.text_input("New Title", value=task["title"], key=f"new_title_{task['_id']}")
                        new_desc = st.text_area("New Description", value=task.get("description", ""), key=f"new_desc_{task['_id']}")
                        if st.button("Save Changes", key=f"save_{task['_id']}"):
                            update_data = {
                                "task_id": task["_id"],
                                "title": new_title,
                                "description": new_desc,
                                "status": task.get("status", "Incomplete")
                            }
                            res = requests.put(f"{API_URL}/todos/", params={"user_email": user_email}, json=update_data)
                            if res.status_code == 200:
                                st.success("Task updated!")
                                st.rerun()
                            else:
                                st.error(res.json().get("detail", "Failed to update"))

                # Delete button
                if col4.button("❌ Delete", key=f"del_{task['_id']}"):
                    res = requests.delete(f"{API_URL}/todos/", params={"user_email": user_email}, json={"task_id": task["_id"]})
                    if res.status_code == 200:
                        st.rerun()
        else:
            st.info("No tasks yet. Add one above!")
    else:
        st.error("Failed to fetch tasks")
