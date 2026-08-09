import { AppBar, Toolbar, Button, Typography } from "@mui/material";
import { Link, Outlet } from "react-router-dom";

export default function Layout() {
  return (
    <>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            AI Site Analyzer
          </Typography>
          <Button color="inherit" component={Link} to="/">
            Upload
          </Button>
          <Button color="inherit" component={Link} to="/dashboard">
            Dashboard
          </Button>
        </Toolbar>
      </AppBar>
      <Outlet />
    </>
  );
}
