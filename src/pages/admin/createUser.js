import React, { useState, useEffect } from "react";
import axios from "axios";
import "../../styles/pages.css";
import { Typography, Button } from "@mui/material";
import validator from "validator";
import {useSnackbar } from 'notistack';

function CreateUser() {

  const { enqueueSnackbar } = useSnackbar();
  const [notification, setNotification] = useState({ message: "", type: "" });
  const [newUser, setNewUser] = useState({
    username: "",
    email: "",
    password: "",
    is_admin: false,
  });

 

  const createUser = async (e) => {
    e.preventDefault();
    if (!newUser.username) {
      enqueueSnackbar("PLease enter username", { variant: "error" });
    } else if (!newUser.email) {
      enqueueSnackbar("PLease enter email", { variant: "error" });
    } else if (!validator.isEmail(newUser.email)) {
      enqueueSnackbar("Please enter valid email", { variant: "error" });
    } else if (!newUser.password) {
      enqueueSnackbar("Please enter password", { variant: "error" });
    } else {
        try {
      await axios.post("/admin/users", newUser);
      setNewUser({ username: "", email: "", password: "", is_admin: false });
     
      showNotification("User created successfully");
    } catch (error) {
      showNotification(
        error.response?.data?.detail || "Error creating user",
        "error"
      );
    }
    }

  
  };
  const showNotification = (message, type = "success") => {
    setNotification({ message, type });
    setTimeout(() => setNotification({ message: "", type: "" }), 3000);
  };


  return (
    <>
      <div className="form">
        <Typography variant="h5" className="bold center-align">
          Create User
        </Typography>
        <form onSubmit={createUser} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Username
            </label>
            <input
              type="text"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              value={newUser.username}
              onChange={(e) =>
                setNewUser({ ...newUser, username: e.target.value })
              }
              // required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Email
            </label>
            <input
              // type="email"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              value={newUser.email}
              onChange={(e) =>
                setNewUser({ ...newUser, email: e.target.value })
              }
              // required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Password
            </label>
            <input
              type="password"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              value={newUser.password}
              onChange={(e) =>
                setNewUser({ ...newUser, password: e.target.value })
              }
              // required
            />
          </div>
          <div className="flex items-center">
            <input
              style={{ width: "auto" }}
              type="checkbox"
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              checked={newUser.is_admin}
              onChange={(e) =>
                setNewUser({ ...newUser, is_admin: e.target.checked })
              }
            />
            <label className="ml-2 block text-sm text-gray-900">Is Admin</label>
          </div>
          {/* <button
                  type="submit"
                  className="w-full bg-blue-500 text-white p-2 rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                > */}
          <Button
            color="primary"
            variant="contained"
            className="w-full"
            type="submit"
            disabled = { (!newUser.username || !newUser.password || !newUser.email) ? true : false}
          >
            Create User
          </Button>
        </form>
      </div>
    </>
  );
}

export default CreateUser;
