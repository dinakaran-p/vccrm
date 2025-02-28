import React, { Suspense } from "react";
import WebRoutes from "./routes";
import AuthProvider from "./context/authProvider";  // Import AuthProvider
import "./styles/index.css";
import "./App.css";

function App() {
  return (
    <AuthProvider>
      <Suspense>
        <WebRoutes />
      </Suspense>
    </AuthProvider>
  );
}

export default App;
