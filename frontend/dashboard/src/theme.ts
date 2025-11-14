import { createTheme } from "@mui/material/styles";

const theme = createTheme({
  palette: {
    primary: {
      main: "#3f51b5", // Indigo
    },
    secondary: {
      main: "#9c27b0", // Purple
    },
    background: {
      default: "linear-gradient(to right, #3f51b5, #9c27b0)",
    },
  },
  typography: {
    fontFamily: "Roboto, sans-serif",
  },
});

export default theme;
