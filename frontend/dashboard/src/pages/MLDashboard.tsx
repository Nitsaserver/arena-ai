import React, { useEffect, useState } from "react";
import {
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Typography,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  Divider,
  Stack,
} from "@mui/material";
import {
  getMLStatus,
  getTrainingHistory,
  retrainModel,
  exportTrainingCSV,
} from "../api";

interface MLStatus {
  trained: boolean;
  samples: number;
  last_trained: string | null;
  model_path: string;
}

interface TrainingRun {
  id: number;
  timestamp: string;
  n_samples: number;
  contamination: number;
  model_path: string;
  notes: string;
}

const MLDashboard: React.FC = () => {
  const [status, setStatus] = useState<MLStatus | null>(null);
  const [history, setHistory] = useState<TrainingRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [training, setTraining] = useState(false);

  const loadData = async () => {
    try {
      const s = await getMLStatus();
      const h = await getTrainingHistory();
      setStatus(s);
      setHistory(h);
    } catch (err) {
      console.error("Error loading ML dashboard:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 10000); // auto refresh every 10s
    return () => clearInterval(interval);
  }, []);

  const handleRetrain = async () => {
    if (!confirm("Retrain model now?")) return;
    setTraining(true);
    try {
      await retrainModel();
      alert("Model retrained successfully!");
      loadData();
    } catch (err) {
      alert("Retrain failed");
      console.error(err);
    }
    setTraining(false);
  };

  const handleExport = () => {
    exportTrainingCSV();
  };

  if (loading) return <CircularProgress />;

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>
        ML Model Dashboard
      </Typography>

      {/* Model Status */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Model Status
          </Typography>

          <Stack direction="row" spacing={3}>
            <Box>
              <Typography variant="body1">Trained:</Typography>
              <Typography variant="h6" color={status?.trained ? "green" : "red"}>
                {status?.trained ? "YES" : "NO"}
              </Typography>
            </Box>

            <Box>
              <Typography variant="body1">Samples:</Typography>
              <Typography variant="h6">{status?.samples}</Typography>
            </Box>

            <Box>
              <Typography variant="body1">Last Trained:</Typography>
              <Typography variant="h6">{status?.last_trained || "—"}</Typography>
            </Box>
          </Stack>

          <Divider sx={{ my: 2 }} />

          <Stack direction="row" spacing={2}>
            <Button
              variant="contained"
              color="primary"
              onClick={handleRetrain}
              disabled={training}
            >
              {training ? "Retraining…" : "Retrain Model"}
            </Button>

            <Button variant="outlined" onClick={handleExport}>
              Export Training CSV
            </Button>
          </Stack>
        </CardContent>
      </Card>

      {/* Training History */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Recent Training Runs
          </Typography>

          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Timestamp</TableCell>
                <TableCell>Samples</TableCell>
                <TableCell>Contamination</TableCell>
                <TableCell>Notes</TableCell>
              </TableRow>
            </TableHead>

            <TableBody>
              {history.map((h) => (
                <TableRow key={h.id}>
                  <TableCell>{h.id}</TableCell>
                  <TableCell>{h.timestamp}</TableCell>
                  <TableCell>{h.n_samples}</TableCell>
                  <TableCell>{h.contamination}</TableCell>
                  <TableCell>{h.notes}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </Box>
  );
};

export default MLDashboard;
