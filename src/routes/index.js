import React from "react";
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  Outlet,
} from "react-router-dom";
import Login from "../pages/auth/login";
import UserDashboard from "pages/user/userDashboard";
import UserSidebar from "pages/layout/user";

import AdminDashboard from "pages/admin/adminDashboard";
import AdminSidebar from "pages/layout/admin.js";
import CreateUser from "pages/admin/createUser";
import CreateTask from "pages/admin/createTask";
import DeadlineTasks from "pages/admin/deallineTasks";
import UpcomingTasks from "pages/admin/upcomingTasks";
import ViewDocs from "pages/admin/viewDocs";
import useAuth from "pages/auth/useAuth"

// ✅ Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { user } = useAuth();
  return user ? children : <Navigate to="/login" />;
};

// ✅ Admin Layout with Sidebar
const AdminLayout = () => {
  return (
    <div style={{ display: "flex" }}>
      <AdminSidebar />
      <div style={{ flex: 1, marginTop: "66px" }}>
        <div  style={{ padding: "50px 0",backgroundColor:'#FFF5E6' }}>
          {/* className="bg-gray-100" */}
          {" "}
          <Outlet />{" "}
        </div>
      </div>
    </div>
  );
};


const UserLayout = () => {
  return (
    <div style={{ display: "flex" }}>
      <UserSidebar />
      <div style={{ flex: 1, marginTop: "66px" }}>
        <div  style={{ padding: "50px 0",backgroundColor:'#FFF5E6' }}>
          <Outlet />
        </div>
      </div>
    </div>
  );
};

const WebRoutes = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />

        <Route
          path="/admin"
          element={
            <ProtectedRoute>
              <AdminLayout />
            </ProtectedRoute>
          }
        >
          <Route path="all-tasks" element={<AdminDashboard />} />
          <Route path="create-user" element={<CreateUser />} />
          <Route path="create-task" element={<CreateTask />} />
          <Route path="deadline-tasks" element={<DeadlineTasks />} />
          <Route path="upcoming-tasks" element={<UpcomingTasks />} />
          <Route path="view-docs" element={<ViewDocs />} />
        </Route>

        <Route
          path="/user"
          element={
            <ProtectedRoute>
              <UserLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<UserDashboard />} />
        </Route>

        <Route path="/" element={<Navigate to="/login" />} />
      </Routes>
    </BrowserRouter>
  );
};

export default WebRoutes;
