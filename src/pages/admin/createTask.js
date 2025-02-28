
import React, { useState, useEffect } from "react";
import axios from "axios";
import { Typography, Button, Box, Tabs, Tab } from "@mui/material";
import validator from "validator";
import { useSnackbar } from "notistack";

function CreateTask() {
  const { enqueueSnackbar } = useSnackbar();

  const [users, setUsers] = useState([]);
  const [tasks, setTasks] = useState([]);
   const [notification, setNotification] = useState({ message: '', type: '' });
  const [file, setFile] = useState(null);
  const [newTask, setNewTask] = useState({
    title: "",
    description: "",
    due_date: "",
    assigned_to: "",
  });

  const [value, setValue] = useState(0);

  const handleChangeTab = (event, newValue) => {
    setValue(newValue);
  };

  const handleChangeTask = (e) => {
    const { name, value } = e.target;
    setNewTask((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const createTask = async (e) => {
    e.preventDefault();

    // ✅ Corrected validation check
    if (!newTask.title) {
      enqueueSnackbar("Please enter Title", { variant: "error" });
      return;
    } else if (!newTask.description) {
      enqueueSnackbar("Please enter Description", { variant: "error" });
      return;
    } else if (!newTask.due_date) { // ✅ Corrected due_date validation
      enqueueSnackbar("Please enter Due Date", { variant: "error" });
      return;
    } else if (!newTask.assigned_to) {
      enqueueSnackbar("Please enter Assignee", { variant: "error" });
      return;
    }

    try {
      const taskData = {
        ...newTask,
        due_date: new Date(newTask.due_date).toISOString(),
        assigned_to: parseInt(newTask.assigned_to),
      };

      console.log("Task Data:", taskData);

      await axios.post("/tasks", taskData);
      setNewTask({ title: "", description: "", due_date: "", assigned_to: "" });

      enqueueSnackbar("Task created successfully", { variant: "success" });
    } catch (error) {
      enqueueSnackbar(error.response?.data?.detail || "Error creating task", {
        variant: "error",
      });
    }
  };


  useEffect(() => {
    fetchTasks();
    fetchUsers();
  }, []);

  const fetchTasks = async () => {
    try {
      const response = await axios.get('/tasks');
      setTasks(response.data);
    } catch (error) {
      showNotification(error.response?.data?.detail || 'Error fetching tasks', 'error');
    }
  };
  const fetchUsers = async () => {
    try {
      const response = await axios.get('/admin/users');
      setUsers(response.data);
    } catch (error) {
      showNotification(error.response?.data?.detail || 'Error fetching users', 'error');
    }
  };

        const showNotification = (message, type = 'success') => {
        setNotification({ message, type });
        setTimeout(() => setNotification({ message: '', type: '' }), 3000);
      };


  return (
    <>
      <Box
        sx={{ width: "100%", bgcolor: "background.paper" }}
        style={{
          maxWidth: "550px",
          margin: "0 auto",
          backgroundColor: "#FFD79C",
          borderRadius: "10px",
          padding: "20px 10px",
        }}
      >
        <Tabs value={value} onChange={handleChangeTab} centered>
          <Tab value={0} label="Create Single Task" />
          <Tab value={1} label="Create Bulk Tasks" />
        </Tabs>

        {value === 0 && (
          <div className="form">
            <Typography variant="h5" className="bold center-align">
              Create Task
            </Typography>
            <form onSubmit={createTask} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Title
                </label>
                <input
                  type="text"
                  name="title"
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  value={newTask.title}
                  onChange={handleChangeTask}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Description
                </label>
                <textarea
                  name="description"
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  value={newTask.description} // ✅ Added missing value
                  onChange={handleChangeTask}
                  rows="3"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Due Date
                </label>
                <input
                   type="date"
                  name="due_date"
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  value={newTask.due_date}
                  onChange={handleChangeTask}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Assign To
                </label>
                <select
                  name="assigned_to"
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  value={newTask.assigned_to}
                  onChange={handleChangeTask}
                >
                  <option value="">Select User</option>
                  {users.map((user) => (
                    <option key={user.id} value={user.id}>
                      {user.username}
                    </option>
                  ))}
                </select>
              </div>
              <Button
                color="primary"
                variant="contained"
                className="w-full"
                type="submit"
                disabled = { (!newTask.title || !newTask.assigned_to || !newTask.description || !newTask.due_date) ? true : false }
              >
                Create Task
              </Button>
            </form>
          </div>
        )}

        {value === 1 && (
          <div className="form">
            <Typography variant="h5" className="bold center-align">
              Create Bulk Tasks
            </Typography>
            <input
              type="file"
              id="myFile"
              name="filename"
              onChange={(event) => setFile(event.target.files[0])}
            />
            <Button
              color="primary"
              variant="contained"
              className="w-full"
              type="submit"
              disabled={!file}

            >
              Upload
            </Button>
          </div>
        )}
      </Box>
    </>
  );
}

export default CreateTask;
