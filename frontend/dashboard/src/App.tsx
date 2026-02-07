import React, { useState } from "react";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";

// External Components
import UsersTable from "./components/UsersTable";
import TeamsTable from "./components/TeamsTable";
import MatchesTable from "./components/MatchesTable";
import MLDashboard from "./pages/MLDashboard";

// -----------------------------
// MUI Imports
// -----------------------------
import {
  Box,
  CssBaseline,
  Drawer,
  AppBar,
  Toolbar,
  IconButton,
  Typography,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Container,
  Avatar,
  useMediaQuery,
  Badge,
  Tooltip,
} from "@mui/material";

import { createTheme, ThemeProvider, styled } from "@mui/material/styles";
import MenuIcon from "@mui/icons-material/Menu";
import DashboardIcon from "@mui/icons-material/Dashboard";
import PeopleIcon from "@mui/icons-material/People";
import GroupWorkIcon from "@mui/icons-material/GroupWork";
import SportsKabaddiIcon from "@mui/icons-material/SportsKabaddi";
import AutoGraphIcon from "@mui/icons-material/AutoGraph";
import HistoryIcon from "@mui/icons-material/History";
import LogoutIcon from "@mui/icons-material/Logout";

// -----------------------------
// Theme (black + neon technical accents)
// -----------------------------
const theme = createTheme({
  palette: {
    mode: "dark",
    background: {
      default: "#050507",
      paper: "#0b0c0e",
    },
    primary: {
      main: "#00bcd4",
    },
    secondary: {
      main: "#7c4dff",
    },
    text: {
      primary: "#e6eef6",
      secondary: "#9fb3c8",
    },
  },
  typography: {
    fontFamily: `Inter, Roboto, -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif`,
  },
});

const drawerWidth = 260;

const LogoBox = styled(Box)(({ theme }) => ({
  display: "flex",
  alignItems: "center",
  gap: 12,
  padding: theme.spacing(2),
}));

// -----------------------------
// Sidebar Item Component
// -----------------------------
const SidebarItem = ({ to, icon, label, badge }: any) => (
  <ListItemButton component={Link} to={to} sx={{ borderRadius: 1, mb: 0.5 }}>
    <ListItemIcon sx={{ color: "primary.main", minWidth: 40 }}>{icon}</ListItemIcon>
    <ListItemText primary={label} primaryTypographyProps={{ color: "text.primary" }} />
    {badge ? <Badge badgeContent={badge} color="secondary" /> : null}
  </ListItemButton>
);

// -----------------------------
// Main Shell (Sidebar + AppBar + Routing)
// -----------------------------
const AppShell: React.FC = () => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const isMobile = useMediaQuery(theme.breakpoints.down("md"));

  const drawer = (
    <Box sx={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <LogoBox>
        <Avatar sx={{ bgcolor: "primary.main" }}>A</Avatar>
        <Box>
          <Typography variant="h6">Arena</Typography>
          <Typography variant="caption" sx={{ color: "text.secondary" }}>
            Cyber Red vs Blue
          </Typography>
        </Box>
      </LogoBox>

      <Divider sx={{ borderColor: "#0f1720" }} />

      <List sx={{ p: 2 }}>
        <SidebarItem to="/" icon={<DashboardIcon />} label="Dashboard" />
        <SidebarItem to="/users" icon={<PeopleIcon />} label="Users" />
        <SidebarItem to="/teams" icon={<GroupWorkIcon />} label="Teams" />
        <SidebarItem to="/matches" icon={<SportsKabaddiIcon />} label="Matches" />
        <SidebarItem to="/ml" icon={<AutoGraphIcon />} label="ML Dashboard" />
        <SidebarItem to="/history" icon={<HistoryIcon />} label="Training History" />
      </List>

      <Box sx={{ flexGrow: 1 }} />

      <Box sx={{ p: 2 }}>
        <Divider sx={{ borderColor: "#0f1720" }} />
        <ListItemButton sx={{ mt: 1, borderRadius: 1 }}>
          <ListItemIcon sx={{ color: "primary.main", minWidth: 40 }}>
            <LogoutIcon />
          </ListItemIcon>
          <ListItemText
            primary="Sign out"
            primaryTypographyProps={{ color: "text.primary" }}
          />
        </ListItemButton>
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: "flex", minHeight: "100vh" }}>
      <CssBaseline />

      {/* Top Navbar */}
      <AppBar position="fixed" sx={{ ml: { md: `${drawerWidth}px` }, background: "#060809" }}>
        <Toolbar>
          {isMobile && (
            <IconButton color="inherit" edge="start" onClick={() => setMobileOpen(true)} sx={{ mr: 2 }}>
              <MenuIcon />
            </IconButton>
          )}
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Arena — Cyber Simulation Platform
          </Typography>
          <Tooltip title="Notifications">
            <IconButton color="inherit">
              <Badge badgeContent={5} color="secondary">
                <AutoGraphIcon />
              </Badge>
            </IconButton>
          </Tooltip>
          <Avatar sx={{ ml: 2 }}>N</Avatar>
        </Toolbar>
      </AppBar>

      {/* Sidebar Drawer */}
      <Box
        component="nav"
        sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}
      >
        <Drawer
          variant={isMobile ? "temporary" : "permanent"}
          open={isMobile ? mobileOpen : true}
          onClose={() => setMobileOpen(false)}
          ModalProps={{ keepMounted: true }}
          sx={{
            "& .MuiDrawer-paper": {
              width: drawerWidth,
              boxSizing: "border-box",
              background: "#060809",
              color: "#e6eef6",
              borderRight: "1px solid rgba(255,255,255,0.03)",
            },
          }}
        >
          {drawer}
        </Drawer>
      </Box>

      {/* Main Content */}
      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <Toolbar />
        <Container maxWidth="xl">
          <Routes>
            <Route path="/" element={<MLDashboard />} />
            <Route path="/users" element={<UsersTable />} />
            <Route path="/teams" element={<TeamsTable />} />
            <Route path="/matches" element={<MatchesTable />} />
            <Route path="/ml" element={<MLDashboard />} />
            <Route path="/history" element={<div><h3>Training History</h3></div>} />
            <Route path="*" element={<MLDashboard />} />
          </Routes>
        </Container>
      </Box>
    </Box>
  );
};

// -----------------------------
// Export wrapped in Theme + Router
export default function App() {
  return (
    <BrowserRouter>
      <ThemeProvider theme={theme}>
        <AppShell />
      </ThemeProvider>
    </BrowserRouter>
  );
}


