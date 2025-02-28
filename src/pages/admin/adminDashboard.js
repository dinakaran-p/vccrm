import React, { useState, useEffect } from "react";
import axios from "axios";
import { styled } from "@mui/material/styles";
import TableCell, { tableCellClasses } from "@mui/material/TableCell";
import {
  TableContainer,
  TableBody,
  TableHead,
  TableRow,
  Paper,
  Typography,
  Table,
  InputLabel,
  FormControl,
} from "@mui/material";
import { TextField, MenuItem, Select } from "@mui/material";
import CalendarComponent from "./tasksCalendar";

// Admin Dashboard Component
const AdminDashboard = () => {
  const [users, setUsers] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [filter, setFilter] = React.useState("");

  const [newTask, setNewTask] = useState({
    title: "",
    description: "",
    due_date: "",
    assigned_to: "",
  });

  const [notification, setNotification] = useState({ message: "", type: "" });

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

  const handleChangeFilter = (event) => {
    setFilter(event.target.value);
  };

  return (
    <>
      <div className="min-h-screen">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Typography variant="h5" className="bold left-align m200">
            All Tasks With Calendar
          </Typography>
          <CalendarComponent data={tasks} />

          <div>
            <Typography variant="h5" className="bold left-align m200">
              All Tasks With table
            </Typography>

            <div style={{ float: "left", margin: "5px 0", display: "flex" }}>
              <TextField
                id="outlined-basic"
                label="search..."
                variant="outlined"
                sx={{
                  height: "38px", // Increase TextField height
                  "& .MuiInputBase-root": {
                    height: "100%", // Ensures the input field fills the height
                  },
                }}
              />
              <FormControl
                style={{ marginLeft: "20px", width: "150px" }}
                size="small"
              >
                <InputLabel id="demo-simple-select-label">
                  Filetr by Status
                </InputLabel>
                <Select
                  labelId="demo-simple-select-label"
                  id="demo-simple-select"
                  value={filter}
                  onChange={handleChangeFilter}
                  sx={{
                    width: "100%", // Ensures Select matches the FormControl width
                  }}
                >
                  <MenuItem value="completed">Completed</MenuItem>
                  <MenuItem value="pending">Pending</MenuItem>
                  <MenuItem value="inProgress">In Progress</MenuItem>
                </Select>
              </FormControl>
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
                    <StyledTableCell className="bold">Title </StyledTableCell>
                    <StyledTableCell className="bold">
                      Assigned To
                    </StyledTableCell>
                    <StyledTableCell className="bold">Due Date</StyledTableCell>
                    <StyledTableCell className="bold">Status</StyledTableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {tasks.length !== 0 ? (
                    tasks.map((row) => (
                      <StyledTableRow key={row.id}>
                        <StyledTableCell className="capitalize">
                          {row.title}
                        </StyledTableCell>
                        <StyledTableCell className="capitalize">
                          {row.assignee}
                        </StyledTableCell>
                        <StyledTableCell className="capitalize">
                          {new Date(row.due_date).toLocaleDateString()}
                        </StyledTableCell>
                        {console.log(row.status, "row.status")}
                        <StyledTableCell
                          className="capitalize"
                          style={{
                            color:
                              row.status === "completed"
                                ? "#3dbb74"
                                : "#ED5A6B",
                          }}
                        >
                          {row.status}
                        </StyledTableCell>
                      </StyledTableRow>
                    ))
                  ) : (
                    <StyledTableCell className="m200 center-align">
                      No tasks found
                    </StyledTableCell>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </div>
        </div>
      </div>
    </>
  );
};

export default AdminDashboard;
