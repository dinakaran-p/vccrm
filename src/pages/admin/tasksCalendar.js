import React, { useState, useEffect } from "react";
import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import axios from "axios";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
} from "@mui/material";

const CalendarComponent = (props) => {
  const [events, setEvents] = useState([]);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState(null);

  console.log(props.data, "props");

  useEffect(() => {
    const data = props.data;
    console.log(data, "data");
    const formattedEvents = data.map((item) => ({
      id: item.id,
      title: item.title,
      date: item.due_date,
      backgroundColor: getStatusColor(item.status), // ✅ Set color dynamically
      color: getStatusColor(item.status),
      borderColor: getStatusColor(item.status),
      extendedProps: {
        status: item.status,
        assignee: item.assignee,
        created_at: item.start,
        creator: item.creator,
        description: item.description,
        file_path: item.file_path,
        due_date : item.due_date
      },
    }));

    setEvents(formattedEvents);
  }, [props]);

  const formatDate = () => {
    const dateString = "2025-03-01T00:00:00+05:30";
    const date = new Date(dateString);

    // Format to dd-mm-yyyy
    const formattedDate = date.toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    });

    return formattedDate;
  };

  // Function to assign colors based on status
  const getStatusColor = (status) => {
    switch (status) {
      case "pending":
        return "red";
      case "completed":
        return "green";
      case "inProgress":
        return "orange";
      default:
        return "blue"; // Default color if no match
    }
  };

  const handleEventClick = (info) => {
    setSelectedEvent(info.event);
    setDialogOpen(true);
  };

  return (
    <div>
      <FullCalendar
        plugins={[dayGridPlugin]}
        initialView="dayGridMonth"
        events={events}
        eventClick={handleEventClick}
        style={{ cursor: "pointer", backgroundColor: "#fff" }}
      />

      {/* MUI Dialog for Event Details */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
        <DialogTitle>
          <b>Event Details</b>
        </DialogTitle>
        <DialogContent>
          {selectedEvent && (
            <>
              <Typography variant="body1">
                <strong>Title:</strong> {selectedEvent.title}
              </Typography>
              <Typography variant="body1">
                <strong>Assigned To:</strong>{" "}
                {selectedEvent.extendedProps?.assignee}
              </Typography>
              <Typography variant="body1">
                <strong>Due Date:</strong> { formatDate(selectedEvent.due_date)}
              </Typography>
              <Typography variant="body1">
                <strong>Status:</strong> {selectedEvent.extendedProps?.status}
              </Typography>
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)} color="primary">
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
};

export default CalendarComponent;
