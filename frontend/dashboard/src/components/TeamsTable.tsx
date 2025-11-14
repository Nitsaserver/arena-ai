import React, { useEffect, useState } from "react";
import {
  Box,
  Button,
  TextField,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
} from "@mui/material";
import { fetchTeams, createTeam, deleteTeam } from "../api";

interface Team {
  id: number;
  name: string;
  description: string;
}

const TeamsTable: React.FC = () => {
  const [teams, setTeams] = useState<Team[]>([]);
  const [loading, setLoading] = useState(true);
  const [newTeam, setNewTeam] = useState({ name: "", description: "" });

  useEffect(() => {
    const loadTeams = async () => {
      try {
        const data = await fetchTeams();
        setTeams(data);
      } catch (err) {
        console.error("Error fetching teams:", err);
      } finally {
        setLoading(false);
      }
    };
    loadTeams();
  }, []);

  const handleCreate = async () => {
    if (!newTeam.name || !newTeam.description)
      return alert("All fields required");
    const res = await createTeam(newTeam);
    setTeams([...teams, res.team]);
    setNewTeam({ name: "", description: "" });
  };

  const handleDelete = async (id: number) => {
    await deleteTeam(id);
    setTeams(teams.filter((t) => t.id !== id));
  };

  if (loading)
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="40vh">
        <CircularProgress />
      </Box>
    );

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Teams
      </Typography>

      <Box display="flex" gap={2} mb={3}>
        <TextField
          label="Team Name"
          variant="outlined"
          value={newTeam.name}
          onChange={(e) => setNewTeam({ ...newTeam, name: e.target.value })}
        />
        <TextField
          label="Description"
          variant="outlined"
          value={newTeam.description}
          onChange={(e) => setNewTeam({ ...newTeam, description: e.target.value })}
        />
        <Button variant="contained" color="primary" onClick={handleCreate}>
          Add Team
        </Button>
      </Box>

      <TableContainer component={Paper} sx={{ borderRadius: 2 }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Name</TableCell>
              <TableCell>Description</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {teams.map((t) => (
              <TableRow key={t.id}>
                <TableCell>{t.id}</TableCell>
                <TableCell>{t.name}</TableCell>
                <TableCell>{t.description}</TableCell>
                <TableCell>
                  <Button color="error" onClick={() => handleDelete(t.id)}>
                    Delete
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default TeamsTable;

