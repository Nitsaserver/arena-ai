import React, { useState } from "react";
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  CircularProgress,
  Alert,
  Stack,
} from "@mui/material";
import ReactMarkdown from "react-markdown";
import { explainWithRAG } from "../api";

const RAGPage: React.FC = () => {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleAsk = async () => {
    if (!question.trim()) {
      setError("Please enter a question");
      return;
    }

    setLoading(true);
    setError("");
    setAnswer("");

    try {
      const result = await explainWithRAG(question);
      setAnswer(result.answer);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to get answer");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>
        🤖 Ask RAG Assistant
      </Typography>
      <Typography variant="body2" color="textSecondary" gutterBottom>
        Ask questions about your system, attacks, defenses, and more.
      </Typography>

      {/* Question Input */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Stack spacing={2}>
            <TextField
              label="Your Question"
              multiline
              rows={3}
              fullWidth
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="e.g., What is a prompt injection attack? Why was IP 192.168.1.100 blocked?"
            />
            <Button
              variant="contained"
              onClick={handleAsk}
              disabled={loading}
              fullWidth
            >
              {loading ? "Thinking..." : "Ask"}
            </Button>
          </Stack>
        </CardContent>
      </Card>

      {/* Error */}
      {error && <Alert severity="error">{error}</Alert>}

      {/* Answer */}
      {answer && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Answer:
            </Typography>
            <Typography
              variant="body1"
              style={{ whiteSpace: "pre-wrap", lineHeight: 1.6 }}
            >
              {answer}
            </Typography>
          </CardContent>
        </Card>
      )}

      {loading && (
        <Box display="flex" justifyContent="center">
          <CircularProgress />
        </Box>
      )}
    </Box>
  );
};

export default RAGPage;
