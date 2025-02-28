import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";
import { Theme } from "./styles/theme";
import { ThemeProvider } from "@mui/material/styles";
import { SnackbarProvider} from "notistack";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <SnackbarProvider
      maxSnack={3}
      anchorOrigin={{ vertical: "top", horizontal: "center" }}
    >
      <ThemeProvider theme={Theme}>
        <App />
      </ThemeProvider>
    </SnackbarProvider>
  </React.StrictMode>
);
