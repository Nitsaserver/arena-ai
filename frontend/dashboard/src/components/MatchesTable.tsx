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
import { fetchMatches, createMatch, deleteMatch } from "../api";

interface Match {
  id: number;
  team_a: string;
  team_b: string;
  score: string;
}

const MatchesTable: React.FC = () => {
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);
  const [newMatch, setNewMatch] = useState({ team_a: "", team_b: "", score: "" });

  useEffect(() => {
    const loadMatches = async () => {
      try {
        const data = await fetchMatches();
        setMatches(data);
      } catch (err) {
        console.error("Error fetching matches:", err);
      } finally {
        setLoading(false);
      }
    };
    loadMatches();
  }, []);

  const handleCreate = async () => {
    if (!newMatch.team_a || !newMatch.team_b || !newMatch.score)
      return alert("All fields required");
    const res = await createMatch(newMatch);
    setMatches([...matches, res.match]);
    setNewMatch({ team_a: "", team_b: "", score: "" });
  };

  const handleDelete = async (id: number) => {
    await deleteMatch(id);
    setMatches(matches.filter((m) => m.id !== id));
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
        Matches
      </Typography>

      <Box display="flex" gap={2} mb={3}>
        <TextField
          label="Team A"
          variant="outlined"
          value={newMatch.team_a}
          onChange={(e) => setNewMatch({ ...newMatch, team_a: e.target.value })}
        />
        <TextField
          label="Team B"
          variant="outlined"
          value={newMatch.team_b}
          onChange={(e) => setNewMatch({ ...newMatch, team_b: e.target.value })}
        />
        <TextField
          label="Score"
          variant="outlined"
          value={newMatch.score}
          onChange={(e) => setNewMatch({ ...newMatch, score: e.target.value })}
        />
        <Button variant="contained" color="primary" onClick={handleCreate}>
          Add Match
        </Button>
      </Box>

      <TableContainer component={Paper} sx={{ borderRadius: 2 }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Team A</TableCell>
              <TableCell>Team B</TableCell>
              <TableCell>Score</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {matches.map((m) => (
              <TableRow key={m.id}>
                <TableCell>{m.id}</TableCell>
                <TableCell>{m.team_a}</TableCell>
                <TableCell>{m.team_b}</TableCell>
                <TableCell>{m.score}</TableCell>
                <TableCell>
                  <Button color="error" onClick={() => handleDelete(m.id)}>
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

export default MatchesTable;
