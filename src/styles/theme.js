import { createTheme } from "@mui/material/styles";

export const Theme = createTheme({
  palette: {
    red: {
      main: "#ED5A6B",
      contrastText: "#fff",
    },
    blue: {
      main: "#2281C7",
      contrastText: "#fff",
    },
    yellow: {
      main: "#FFD79C",
      contrastText: "#fff",
    },

    background: {
      grey: "#757575",
      darkGreen: "#33691E",
      lightBlue: "#4E66A1",
      darkBlue: "#06225C",
      lightYellow: "#E4C045",
      darkYellow: "#E1AB3B",
      darkerYellow: "#DA8529",
      lightPink: "#E6E9F1",
    },
  },
  typography: {
    h1: {
      fontSize: "62px",
      //  fontSize: { md: '45px', sm: '2.5rem', xs: '2rem' },
      lineHeight: "61px",
      width: "100%",
      // margin: " 60px auto",
    },
    h2: {
      fontSize: "48px",
      lineHeight: "50px",
      fontStyle: "normal",
    },
    h3: {
      lineHeight: "48px",
      fontSize: "36px",
      // fontSize: { md: '35px', sm: '2.5rem', xs: '2rem' },
      // marginBotton:'20px'
    },

    h4: {
      fontSize: "32px",
      lineHeight: "36px",
    },
    h5: {
      fontSize: "24px",
      lineHeight: "30px",
    },
    h6: {
      fontSize: "18px",
      lineHeight: "20px",
    },

    text: {

      fontStyle: "normal",
      fontWeight: 400,
      fontSize: "16px",
      lineHeight: "26px",
    },
    text2: {
      fontSize: "14px",
      lineHeight: "24px",
    },
    text3: {
      fontSize: "12px",
      lineHeight: "20px",
    },
  },

  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: "initial",
          borderRadius: "10px",
          boxShadow: "none",
          // border: '1px solid #000',
          // padding:'0 30px'
          padding: "8px 30px",
          color:"#ffffff",
          backgroundColor:"#ED5A6B",
          margin:"20px auto"
        },
        primary: {
          color: "#ED5A6B",
        },
      },
    },
    MuiTabs: {
      styleOverrides: {
        indicator: {
          background: "#25468A",
        },
      },
    },
    MuiInputBase: {
      styleOverrides: {
        inputSizeSmall: {
          fontSize: "14px",
          lineHeight: "20px",
        },
      },
    },
  },
});
