import React, { useState, useEffect } from "react";
import useAuth from "../auth/useAuth";
import logo from "assets/images/logo.jpeg";
import { Button} from "@mui/material";
import { Visibility, VisibilityOff } from "@mui/icons-material";
import validator from "validator";
import {useSnackbar } from 'notistack';

// Login Component
const Login = () => {

  const { enqueueSnackbar } = useSnackbar();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const { login, googleLogin } = useAuth();
  const [showPassword, setShowPassword] = useState(false);

  // Initialize Google Sign-In
  useEffect(() => {
    const script = document.createElement("script");
    script.src = "https://accounts.google.com/gsi/client";
    script.async = true;
    script.defer = true;
    document.body.appendChild(script);

    script.onload = () => {
      if (window.google) {
        window.google.accounts.id.initialize({
          client_id: "YOUR_GOOGLE_CLIENT_ID", // Replace with your actual Google Client ID
          callback: handleGoogleCallback,
          auto_select: false,
          cancel_on_tap_outside: true,
          context: "signin",
          ux_mode: "popup",
          login_uri: "http://localhost:8000/auth/google/login",
          redirect_uri: "http://localhost:3000/login",
        });

        window.google.accounts.id.renderButton(
          document.getElementById("googleSignInDiv"),
          {
            theme: "outline",
            size: "large",
            width: "100%",
            text: "continue_with",
            shape: "rectangular",
            locale: "en",
          }
        );
      }
    };

    return () => {
      if (document.body.contains(script)) {
        document.body.removeChild(script);
      }
    };
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();

    console.log()
    
    if (!email) {
      enqueueSnackbar('PLease enter email', { variant:"error" });
    } else if (! validator.isEmail(email)) {
      enqueueSnackbar('Please enter valid email', { variant:"error"  });
    } else if (!password) {
      enqueueSnackbar('Please enter password', { variant:"error"  });
    } else {
      setIsLoading(true);
      setError("");
      try {
        await login(email, password);
      } catch (err) {
        setError(err.toString());
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleGoogleCallback = async (response) => {
    try {
      setIsLoading(true);
      setError("");
      console.log("Google response:", response);

      if (response.credential) {
        await googleLogin(response.credential);
      } else {
        throw new Error("No credential received from Google");
      }
    } catch (err) {
      console.error("Google callback error:", err);
      setError(err.toString());
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="max-w-md w-full bg-white p-8 rounded-lg shadow-lg">
        <div className="center-container">
          <img src={logo} alt="Logo" className="w-[215px] h-[100px]" />
          <h2 className="text-3xl font-bold mb-6 text-center text-gray-800">
            Compliance Management
          </h2>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6 ceter-align">
          <div>
            <label className="block text-gray-700 text-sm font-bold mb-2">
              Email
            </label>
            <input
              // type="email"
              className="w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={isLoading}
            />
          </div>
          {/* <div>
              <label className="block text-gray-700 text-sm font-bold mb-2">
                Password
              </label>
              <input
                type="password"
                className="w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={isLoading}
              />
            </div> */}
          <div className="relative w-full">
            <label className="block text-gray-700 text-sm font-bold mb-2">
              Password
            </label>
            <div className="flex items-center bg-white border border-gray-300 rounded-lg focus-within:ring-2 focus-within:ring-blue-500">
              <input
                style={{ border: "none" }}
                type={showPassword ? "text" : "password"}
                className="w-full p-3 focus:outline-none bg-transparent"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={isLoading}
              />
              <button
                type="button"
                style={{ border: "none", backgroundColor: "#ffffff" }}
                className="p-2 text-gray-500 hover:text-gray-700 focus:outline-none"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? (
                  <VisibilityOff fontSize="small" />
                ) : (
                  <Visibility fontSize="small" />
                )}
              </button>
            </div>
          </div>
          <Button
            color="primary"
            variant="contained"
            className="w-full"
            type="submit"
            // onClick={() => setIsLoading(true)}
            // type="submit"
            // className="w-full  text-white p-3 rounded-lg font-semibold
            //          hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
            //          disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={isLoading || ((!email || !password) ? true : false)}
          >
            {isLoading ? "Logging in..." : "Login"}
          </Button>

          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-gray-500">
                Or continue with
              </span>
            </div>
          </div>

          <div id="googleSignInDiv" className="w-full"></div>
        </form>
      </div>
    </div>
  );
};

export default Login;
