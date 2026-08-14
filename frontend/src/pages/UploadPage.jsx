import { useState } from "react";
import {
  Alert,
  Button,
  Container,
  MenuItem,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";

import { createAnalysis } from "../api/analysisApi";
import ResultCard from "../components/ResultCard";
import {
  ALLOWED_IMAGE_TYPES,
  ANALYSIS_TYPE_OPTIONS,
  IMAGE_SOURCE_OPTIONS,
  MAX_FILE_SIZE_BYTES,
} from "../constants";

const EMPTY_FORM = {
  siteName: "",
  captureDatetime: "",
  imageSource: "",
  analysisType: "",
  file: null,
};

function validate(form) {
  const errors = {};

  if (!form.siteName.trim()) errors.siteName = "Site name is required.";
  if (!form.captureDatetime) errors.captureDatetime = "Capture date/time is required.";
  if (!form.imageSource) errors.imageSource = "Image source is required.";
  if (!form.analysisType) errors.analysisType = "Analysis type is required.";

  if (!form.file) {
    errors.file = "An image file is required.";
  } else if (!ALLOWED_IMAGE_TYPES.includes(form.file.type)) {
    errors.file = "Unsupported file type. Allowed: JPEG, PNG, WEBP.";
  } else if (form.file.size > MAX_FILE_SIZE_BYTES) {
    errors.file = `File too large. Max size is ${MAX_FILE_SIZE_BYTES / (1024 * 1024)}MB.`;
  }

  return errors;
}

export default function UploadPage() {
  const [form, setForm] = useState(EMPTY_FORM);
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);
  const [result, setResult] = useState(null);

  function updateField(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  function handleReset() {
    setForm(EMPTY_FORM);
    setErrors({});
    setSubmitError(null);
    setResult(null);
  }

  async function handleSubmit(event) {
    event.preventDefault();

    const validationErrors = validate(form);
    setErrors(validationErrors);
    if (Object.keys(validationErrors).length > 0) return;

    setSubmitting(true);
    setSubmitError(null);
    try {
      const response = await createAnalysis(form);
      setResult(response.data);
    } catch (error) {
      const detail = error.response?.data?.detail;
      setSubmitError(
        typeof detail === "string"
          ? detail
          : "Something went wrong submitting the analysis. Please try again."
      );
    } finally {
      setSubmitting(false);
    }
  }

  if (result) {
    return (
      <Container maxWidth="sm" sx={{ py: 4 }}>
        <Stack spacing={2}>
          <ResultCard analysis={result} showImage />
          <Button variant="outlined" onClick={handleReset}>
            Analyze another
          </Button>
        </Stack>
      </Container>
    );
  }

  return (
    <Container maxWidth="sm" sx={{ py: 4 }}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          AI Site Analyzer
        </Typography>

        <Stack component="form" spacing={2} onSubmit={handleSubmit} noValidate>
          <TextField
            label="Site Name"
            value={form.siteName}
            onChange={(e) => updateField("siteName", e.target.value)}
            error={!!errors.siteName}
            helperText={errors.siteName}
          />

          <TextField
            label="Capture Date & Time"
            type="datetime-local"
            slotProps={{ inputLabel: { shrink: true } }}
            value={form.captureDatetime}
            onChange={(e) => updateField("captureDatetime", e.target.value)}
            error={!!errors.captureDatetime}
            helperText={errors.captureDatetime}
          />

          <TextField
            select
            label="Image Source"
            value={form.imageSource}
            onChange={(e) => updateField("imageSource", e.target.value)}
            error={!!errors.imageSource}
            helperText={errors.imageSource}
          >
            {IMAGE_SOURCE_OPTIONS.map((option) => (
              <MenuItem key={option.value} value={option.value}>
                {option.label}
              </MenuItem>
            ))}
          </TextField>

          <TextField
            select
            label="Analysis Type"
            value={form.analysisType}
            onChange={(e) => updateField("analysisType", e.target.value)}
            error={!!errors.analysisType}
            helperText={errors.analysisType}
          >
            {ANALYSIS_TYPE_OPTIONS.map((option) => (
              <MenuItem key={option.value} value={option.value}>
                {option.label}
              </MenuItem>
            ))}
          </TextField>

          <Button component="label" variant="outlined">
            {form.file ? form.file.name : "Choose Image"}
            <input
              type="file"
              hidden
              accept={ALLOWED_IMAGE_TYPES.join(",")}
              onChange={(e) => updateField("file", e.target.files[0] ?? null)}
            />
          </Button>
          {errors.file && (
            <Typography color="error" variant="caption">
              {errors.file}
            </Typography>
          )}

          {submitError && <Alert severity="error">{submitError}</Alert>}

          <Button type="submit" variant="contained" disabled={submitting}>
            {submitting ? "Analyzing..." : "Run Analysis"}
          </Button>
        </Stack>
      </Paper>
    </Container>
  );
}
