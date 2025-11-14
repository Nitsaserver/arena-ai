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
import { fetchUsers, createUser, deleteUser } from "../api";

interface User {
  id: number;
  username: string;
  email: string;
}

const UsersTable: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [newUser, setNewUser] = useState({ username: "", email: "" });

  useEffect(() => {
    const loadUsers = async () => {
      try {
        const data = await fetchUsers();
        setUsers(data);
      } catch (err) {
        console.error("Error fetching users:", err);
      } finally {
        setLoading(false);
      }
    };
    loadUsers();
  }, []);

  const handleCreate = async () => {
    if (!newUser.username || !newUser.email) return alert("All fields required");
    const res = await createUser(newUser);
    setUsers([...users, res.user]);
    setNewUser({ username: "", email: "" });
  };

  const handleDelete = async (id: number) => {
    await deleteUser(id);
    setUsers(users.filter((u) => u.id !== id));
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
        Users
      </Typography>

      <Box display="flex" gap={2} mb={3}>
        <TextField
          label="Username"
          variant="outlined"
          value={newUser.username}
          onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
        />
        <TextField
          label="Email"
          variant="outlined"
          value={newUser.email}
          onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
        />
        <Button variant="contained" color="primary" onClick={handleCreate}>
          Add User
        </Button>
      </Box>

      <TableContainer component={Paper} sx={{ borderRadius: 2 }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Username</TableCell>
              <TableCell>Email</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {users.map((u) => (
              <TableRow key={u.id}>
                <TableCell>{u.id}</TableCell>
                <TableCell>{u.username}</TableCell>
                <TableCell>{u.email}</TableCell>
                <TableCell>
                  <Button color="error" onClick={() => handleDelete(u.id)}>
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

export default UsersTable;



