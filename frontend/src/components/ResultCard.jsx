import {
  Alert,
  Card,
  CardContent,
  Chip,
  Divider,
  Stack,
  Typography,
} from "@mui/material";

function ClassificationDetails({ result }) {
  return (
    <Stack spacing={1}>
      <Typography>
        Category: <strong>{result.category}</strong> ({Math.round(result.confidence * 100)}%)
      </Typography>
      {result.alternatives?.length > 0 && (
        <Stack direction="row" spacing={1}>
          {result.alternatives.map((alt) => (
            <Chip
              key={alt.category}
              label={`${alt.category} (${Math.round(alt.confidence * 100)}%)`}
              variant="outlined"
            />
          ))}
        </Stack>
      )}
    </Stack>
  );
}

function VehicleDetectionDetails({ result }) {
  return (
    <Stack spacing={1}>
      <Typography>
        Vehicles detected: <strong>{result.total_count}</strong>
      </Typography>
      <Stack direction="row" spacing={1} flexWrap="wrap">
        {Object.entries(result.count_by_type)
          .filter(([, count]) => count > 0)
          .map(([type, count]) => (
            <Chip key={type} label={`${type}: ${count}`} variant="outlined" />
          ))}
      </Stack>
    </Stack>
  );
}

function ImageQualityDetails({ result }) {
  return (
    <Stack spacing={1}>
      <Typography>
        Quality: <strong>{result.quality}</strong>
      </Typography>
      <Stack direction="row" spacing={1}>
        <Chip
          label={result.is_blurry ? "Blurry" : "Sharp"}
          color={result.is_blurry ? "warning" : "success"}
        />
        <Chip
          label={result.is_dark ? "Dark" : "Well-lit"}
          color={result.is_dark ? "warning" : "success"}
        />
      </Stack>
    </Stack>
  );
}

const DETAILS_BY_TYPE = {
  classification: ClassificationDetails,
  vehicle_detection: VehicleDetectionDetails,
  image_quality: ImageQualityDetails,
};

export default function ResultCard({ analysis }) {
  if (analysis.status === "failed") {
    return (
      <Card variant="outlined">
        <CardContent>
          <Typography variant="h6" gutterBottom>
            {analysis.site_name}
          </Typography>
          <Alert severity="error">{analysis.error_message}</Alert>
        </CardContent>
      </Card>
    );
  }

  const DetailsComponent = DETAILS_BY_TYPE[analysis.analysis_type];

  return (
    <Card variant="outlined">
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {analysis.site_name}
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          {analysis.analysis_type} &middot; {analysis.processing_time_ms}ms
        </Typography>
        <Divider sx={{ my: 1 }} />
        {DetailsComponent && <DetailsComponent result={analysis.result} />}
      </CardContent>
    </Card>
  );
}
