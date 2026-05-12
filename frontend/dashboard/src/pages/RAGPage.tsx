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

      <Typography
        variant="body2"
        color="text.secondary"
        gutterBottom
        sx={{ mb: 3 }}
      >
        Ask questions about your system, attacks, defenses, and more.
      </Typography>

      {/* Question Input */}
      <Card sx={{ mb: 3, background: "#0b0c0e" }}>
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
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Loading */}
      {loading && (
        <Box display="flex" justifyContent="center" mt={3}>
          <CircularProgress />
        </Box>
      )}

      {/* Answer */}
      {answer && (
        <Card sx={{ background: "#0b0c0e" }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Answer
            </Typography>

            <Box
              sx={{
                lineHeight: 1.8,
                color: "#d1d5db",

                "& p": {
                  mb: 2,
                },

                "& h1, & h2, & h3": {
                  color: "#ffffff",
                  mt: 3,
                  mb: 2,
                },

                "& ul": {
                  pl: 3,
                  mb: 2,
                },

                "& li": {
                  mb: 1,
                },

                "& strong": {
                  color: "#ffffff",
                },

                "& code": {
                  backgroundColor: "#111827",
                  padding: "2px 6px",
                  borderRadius: "4px",
                  color: "#00bcd4",
                  fontFamily: "monospace",
                },
              }}
            >
              <ReactMarkdown>{answer}</ReactMarkdown>
            </Box>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default RAGPage;