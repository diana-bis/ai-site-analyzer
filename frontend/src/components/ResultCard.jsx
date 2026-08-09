import {
  Alert,
  Box,
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
        {result.detections.map((detection, index) => (
          <Chip
            key={index}
            label={`${detection.vehicle_type} (${Math.round(detection.confidence * 100)}%)`}
            variant="outlined"
          />
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

// Boxes are normalized (0-1 fractions), so they're positioned with plain
// CSS percentages - no JS measuring of the rendered image size needed.
function BoundingBoxOverlay({ detections }) {
  return detections.map((detection, index) => (
    <Box
      key={index}
      sx={{
        position: "absolute",
        left: `${detection.bounding_box.x * 100}%`,
        top: `${detection.bounding_box.y * 100}%`,
        width: `${detection.bounding_box.width * 100}%`,
        height: `${detection.bounding_box.height * 100}%`,
        border: "2px solid #d32f2f",
        boxSizing: "border-box",
      }}
    />
  ));
}

export default function ResultCard({ analysis, showImage = false }) {
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
  const imageUrl = `${import.meta.env.VITE_API_BASE_URL}/api/analysis/${analysis.id}/image`;

  return (
    <Card variant="outlined">
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {analysis.site_name}
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          {analysis.analysis_type} &middot; {analysis.processing_time_ms}ms
        </Typography>

        {showImage && (
          <Box sx={{ position: "relative", mb: 2, lineHeight: 0 }}>
            <img src={imageUrl} alt={analysis.site_name} style={{ width: "100%" }} />
            {analysis.analysis_type === "vehicle_detection" && (
              <BoundingBoxOverlay detections={analysis.result.detections} />
            )}
          </Box>
        )}

        <Divider sx={{ my: 1 }} />
        {DetailsComponent && <DetailsComponent result={analysis.result} />}
      </CardContent>
    </Card>
  );
}
