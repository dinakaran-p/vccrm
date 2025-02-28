import { useContext } from "react";
import { AuthContext } from "../../context/authProvider";
import { useNavigate } from "react-router-dom";
import axios from "axios";

// Axios configuration - using FastAPI port 8000
axios.defaults.baseURL = `https://ajvc.dinakaranpalani.xyz/api`;
//  'http://localhost:8000'; 

const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }

  const { user, setUser } = context;
  const navigate = useNavigate();

  const handleAuthSuccess = (data) => {
    const { access_token, user_id, is_admin } = data;

    axios.defaults.headers.common["Authorization"] = `Bearer ${access_token}`;

    localStorage.setItem("token", access_token);
    localStorage.setItem("isAdmin", is_admin);
    localStorage.setItem("userId", user_id);

    setUser({
      token: access_token,
      id: user_id,
      isAdmin: is_admin,
    });

    navigate(is_admin ? "/admin/all-tasks" : "/user");
  };

  const login = async (email, password) => {
    try {
      const response = await axios.post("/auth/login", { email, password });
      handleAuthSuccess(response.data);
    } catch (error) {
      throw error.response?.data?.detail || "Login failed.";
    }
  };

  const googleLogin = async (googleToken) => {
    try {
      const response = await axios.post("/auth/google/login", {
        token: googleToken,
      });
      handleAuthSuccess(response.data);
    } catch (error) {
      throw error.response?.data?.detail || "Google login failed.";
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem("token");
    localStorage.removeItem("isAdmin");
    localStorage.removeItem("userId");
    delete axios.defaults.headers.common["Authorization"];
    navigate("/login");
  };

  return { user, login, googleLogin, logout };
};

export default useAuth;
