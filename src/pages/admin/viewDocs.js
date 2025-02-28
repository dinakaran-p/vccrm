import React, { useState, useEffect } from "react";
import axios from "axios";
import { styled } from "@mui/material/styles";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell, { tableCellClasses } from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Paper from "@mui/material/Paper";
import { Button, Typography } from "@mui/material";
import {  TextField,MenuItem,Select} from '@mui/material';

// Admin Dashboard Component
const Docs = () => {
  const [users, setUsers] = useState([]);
  const [tasks, setTasks] = useState([]);

  const [newTask, setNewTask] = useState({
    title: "",
    description: "",
    due_date: "",
    assigned_to: "",
  });

  const [notification, setNotification] = useState({ message: "", type: "" });
   const [filter, setFilter] = React.useState('');
    const handleChangeFilter = (event) => {
      setFilter(event.target.value);
    };

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      const response = await axios.get("/tasks");
      setTasks(response.data);
    } catch (error) {
      showNotification(
        error.response?.data?.detail || "Error fetching tasks",
        "error"
      );
    }
  };

  const showNotification = (message, type = "success") => {
    setNotification({ message, type });
    setTimeout(() => setNotification({ message: "", type: "" }), 3000);
  };

  const StyledTableCell = styled(TableCell)(({ theme }) => ({
    [`&.${tableCellClasses.head}`]: {
      // backgroundColor: theme.palette.common.black,
      // color: theme.palette.common.white,
      textAlign: "center",
      border: "1px solid #ededed",
    },
    [`&.${tableCellClasses.body}`]: {
      fontSize: 14,
      textAlign: "center",
      border: "1px solid #ededed !important",
    },
  }));

  const StyledTableRow = styled(TableRow)(({ theme }) => ({
    "&:nth-of-type(odd)": {
      backgroundColor: theme.palette.action.hover,
    },
    // hide last border
    "&:last-child td, &:last-child th": {
      border: 0,
    },
  }));



  return (
    <>
      <div className="min-h-screen" >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Typography variant="h5" className="bold left-align m200" >View Documents</Typography>
        <div style={{ float: "right", margin: "5px 0", display: "flex" }}>
            <TextField
              id="outlined-basic"
              label="search..."
              variant="outlined"
            />
            <Select style={{marginLeft:"20px",width:"100px"}}
              labelId="demo-simple-select-label"
              id="demo-simple-select"
              value={filter}
              label="filter"
              onChange={handleChangeFilter}
            >
              <MenuItem value={10}>completed</MenuItem>
              <MenuItem value={20}>Pending</MenuItem>
              <MenuItem value={30}>In Progress</MenuItem>
            </Select>
          </div>
          {notification.message && (
            <div
              className={`mb-4 p-4 rounded-lg ${
                notification.type === "error"
                  ? "bg-red-100 text-red-700"
                  : "bg-green-100 text-green-700"
              }`}
            >
              {notification.message}
            </div>
          )}

          <TableContainer component={Paper}>
            <Table sx={{ minWidth: 700 }} aria-label="customized table">
              <TableHead>
                <TableRow>
                  <StyledTableCell className="bold">User </StyledTableCell>
                  <StyledTableCell className="bold">Task</StyledTableCell>
                  <StyledTableCell className="bold">document</StyledTableCell>
                  <StyledTableCell className="bold">Action</StyledTableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {tasks.length !== 0 ? tasks.map((row) => (
                  <StyledTableRow key={row.id}>
                     <StyledTableCell className="capitalize">{row.assignee}</StyledTableCell>
                    <StyledTableCell className="capitalize">{row.title}</StyledTableCell>
                    <StyledTableCell className="capitalize" style={{color: row.status === "completed" ? "#3dbb74" : "#ED5A6B" }}>{row.status}</StyledTableCell>
                    <StyledTableCell>
                        <Button variant="contained" color="primary" style={{margin:'0px'}}>View</Button>
                    </StyledTableCell>
                  </StyledTableRow>
                )) :<div className="m200 center-align">No tasks found</div> }
              </TableBody>
            </Table>
          </TableContainer>
        </div>
      </div>
    </>
  );
};

export default Docs;
