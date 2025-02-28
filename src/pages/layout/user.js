import * as React from "react";
import AppBar from "@mui/material/AppBar";
import Box from "@mui/material/Box";
import CssBaseline from "@mui/material/CssBaseline";
import Divider from "@mui/material/Divider";
import Drawer from "@mui/material/Drawer";
import IconButton from "@mui/material/IconButton";
import MenuIcon from "@mui/icons-material/Menu";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import { NavLink } from "react-router-dom";
import useAuth from "../auth/useAuth";
import LogoutIcon from "@mui/icons-material/Logout";
import logo from "assets/images/logo.jpeg";

export default function ResponsiveDrawer(props) {
  const { window } = props;
  const [mobileOpen, setMobileOpen] = React.useState(false);
  const [isClosing, setIsClosing] = React.useState(false);
  const { logout } = useAuth();

  const handleDrawerToggle = () => {
    if (!isClosing) {
      setMobileOpen(!mobileOpen);
    }
  };

  return (
    <Box sx={{ display: "flex" }}>
      <CssBaseline />

      <AppBar
        style={{ backgroundColor: "  #2281C7", display: "flex" }}
        position="fixed"
        // sx={{
        //   width: { sm: `calc(100% - ${drawerWidth}px)` },
        //   ml: { sm: `${drawerWidth}px` },
        // }}
      >
        <Toolbar>
          <div>
            <img
              src={logo}
              alt=""
              style={{ maxWidth: "100px", maxHeight: "50px", margin: "0 30px" }}
            />
          </div>
          <Typography variant="h4" noWrap component="div" sx={{ flexGrow: 1 }}>
            Compliance Management
          </Typography>
          <LogoutIcon onClick={logout}  style={{cursor:'pointer'}}/>         
        </Toolbar>
      </AppBar>
    </Box>
  );
}
