import { useEffect, useState } from "react";
import {
  Alert,
  Box,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Container,
  Grid,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import { useNavigate } from "react-router-dom";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { getDashboard } from "../api/dashboardApi";

const PIE_COLORS = ["#1976d2", "#9c27b0", "#2e7d32", "#ed6c02", "#d32f2f", "#0288d1"];

function KpiCard({ label, value }) {
  return (
    <Card variant="outlined">
      <CardContent>
        <Typography variant="body2" color="text.secondary">
          {label}
        </Typography>
        <Typography variant="h4">{value}</Typography>
      </CardContent>
    </Card>
  );
}

function AnalysesTable({ rows, emptyMessage }) {
  const navigate = useNavigate();

  if (rows.length === 0) {
    return <Typography color="text.secondary">{emptyMessage}</Typography>;
  }

  return (
    <Table size="small">
      <TableHead>
        <TableRow>
          <TableCell>Site</TableCell>
          <TableCell>Type</TableCell>
          <TableCell>Status</TableCell>
          <TableCell>Created</TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {rows.map((row) => (
          <TableRow
            key={row.id}
            hover
            onClick={() => navigate(`/analysis/${row.id}`)}
            sx={{ cursor: "pointer" }}
          >
            <TableCell>{row.site_name}</TableCell>
            <TableCell>{row.analysis_type}</TableCell>
            <TableCell>
              <Chip
                size="small"
                label={row.status}
                color={row.status === "failed" ? "error" : "success"}
              />
            </TableCell>
            <TableCell>{new Date(row.created_at).toLocaleString()}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

export default function DashboardPage() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    getDashboard()
      .then((response) => setData(response.data))
      .catch(() => setError("Could not load dashboard data."));
  }, []);

  if (error) {
    return (
      <Container sx={{ py: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  if (!data) {
    return (
      <Container sx={{ py: 4, textAlign: "center" }}>
        <CircularProgress />
      </Container>
    );
  }

  if (data.total_analyses === 0) {
    return (
      <Container sx={{ py: 4 }}>
        <Alert severity="info">No analyses yet. Run one from the Upload page.</Alert>
      </Container>
    );
  }

  const byTypeData = Object.entries(data.by_analysis_type).map(([name, count]) => ({
    name,
    count,
  }));
  const byCategoryData = Object.entries(data.by_category).map(([name, value]) => ({
    name,
    value,
  }));

  return (
    <Container sx={{ py: 4 }}>
      <Typography variant="h5" gutterBottom>
        Dashboard
      </Typography>

      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid size={{ xs: 6, sm: 3 }}>
          <KpiCard label="Total Analyses" value={data.total_analyses} />
        </Grid>
        <Grid size={{ xs: 6, sm: 3 }}>
          <KpiCard label="Total Detections" value={data.total_detections} />
        </Grid>
        <Grid size={{ xs: 6, sm: 3 }}>
          <KpiCard
            label="Avg Processing Time"
            value={data.average_processing_time_ms != null ? `${data.average_processing_time_ms}ms` : "-"}
          />
        </Grid>
        <Grid size={{ xs: 6, sm: 3 }}>
          <KpiCard
            label="Avg Confidence"
            value={data.average_confidence_score != null ? `${Math.round(data.average_confidence_score * 100)}%` : "-"}
          />
        </Grid>
      </Grid>

      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid size={{ xs: 12, md: 6 }}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              By Analysis Type
            </Typography>
            <Box sx={{ height: 250 }}>
              <ResponsiveContainer>
                <BarChart data={byTypeData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis allowDecimals={false} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#1976d2" />
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </Paper>
        </Grid>

        <Grid size={{ xs: 12, md: 6 }}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              By Category
            </Typography>
            <Box sx={{ height: 250 }}>
              {byCategoryData.length === 0 ? (
                <Typography color="text.secondary">No categorized results yet.</Typography>
              ) : (
                <ResponsiveContainer>
                  <PieChart>
                    <Pie data={byCategoryData} dataKey="value" nameKey="name" outerRadius={80} label>
                      {byCategoryData.map((entry, index) => (
                        <Cell key={entry.name} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </Box>
          </Paper>
        </Grid>
      </Grid>

      <Grid container spacing={2}>
        <Grid size={{ xs: 12, md: 6 }}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Recent Analyses
            </Typography>
            <AnalysesTable rows={data.recent_analyses} emptyMessage="No analyses yet." />
          </Paper>
        </Grid>

        <Grid size={{ xs: 12, md: 6 }}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Failed Analyses
            </Typography>
            <AnalysesTable rows={data.failed_analyses} emptyMessage="No failed analyses." />
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
}
