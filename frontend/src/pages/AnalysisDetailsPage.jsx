import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import {
  Alert,
  CircularProgress,
  Container,
  Paper,
  Stack,
  Typography,
} from "@mui/material";

import { getAnalysisById } from "../api/analysisApi";
import ResultCard from "../components/ResultCard";

export default function AnalysisDetailsPage() {
  const { id } = useParams();
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    setAnalysis(null);
    setError(null);
    getAnalysisById(id)
      .then((response) => setAnalysis(response.data))
      .catch((err) => {
        setError(
          err.response?.status === 404
            ? `Analysis ${id} was not found.`
            : "Could not load this analysis."
        );
      });
  }, [id]);

  if (error) {
    return (
      <Container sx={{ py: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  if (!analysis) {
    return (
      <Container sx={{ py: 4, textAlign: "center" }}>
        <CircularProgress />
      </Container>
    );
  }

  return (
    <Container maxWidth="sm" sx={{ py: 4 }}>
      <Stack spacing={2}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="body2" color="text.secondary">
            Capture time: {new Date(analysis.capture_datetime).toLocaleString()}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Image source: {analysis.image_source}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Uploaded: {new Date(analysis.created_at).toLocaleString()} ({analysis.original_filename})
          </Typography>
        </Paper>

        <ResultCard analysis={analysis} showImage />
      </Stack>
    </Container>
  );
}
