import React, { useEffect, useState } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  CircularProgress,
} from '@mui/material';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { Bar, Doughnut } from 'react-chartjs-2';
import { bugAPI } from '../services/api';
import { useBugStore } from '../store/bugStore';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const Dashboard = () => {
  const { bugs, fetchBugs } = useBugStore();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        await fetchBugs();
        const statsResponse = await bugAPI.getStats();
        setStats(statsResponse.data);
      } catch (error) {
        console.error('Failed to load dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, [fetchBugs]);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  const statusData = {
    labels: ['Open', 'In Progress', 'Resolved', 'Closed'],
    datasets: [
      {
        data: [
          stats?.statusCounts?.open || 0,
          stats?.statusCounts?.inProgress || 0,
          stats?.statusCounts?.resolved || 0,
          stats?.statusCounts?.closed || 0,
        ],
        backgroundColor: [
          '#f44336',
          '#ff9800',
          '#4caf50',
          '#9e9e9e',
        ],
        borderWidth: 2,
      },
    ],
  };

  const priorityData = {
    labels: ['Low', 'Medium', 'High', 'Critical'],
    datasets: [
      {
        label: 'Bugs by Priority',
        data: [
          stats?.priorityCounts?.low || 0,
          stats?.priorityCounts?.medium || 0,
          stats?.priorityCounts?.high || 0,
          stats?.priorityCounts?.critical || 0,
        ],
        backgroundColor: [
          '#4caf50',
          '#ff9800',
          '#f44336',
          '#9c27b0',
        ],
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
    },
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Bugs
              </Typography>
              <Typography variant="h4">
                {stats?.totalBugs || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Open Bugs
              </Typography>
              <Typography variant="h4" color="error">
                {stats?.statusCounts?.open || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                In Progress
              </Typography>
              <Typography variant="h4" color="warning.main">
                {stats?.statusCounts?.inProgress || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Resolved
              </Typography>
              <Typography variant="h4" color="success.main">
                {stats?.statusCounts?.resolved || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Bugs by Status
            </Typography>
            <Box sx={{ height: 300 }}>
              <Doughnut data={statusData} options={chartOptions} />
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Bugs by Priority
            </Typography>
            <Box sx={{ height: 300 }}>
              <Bar data={priorityData} options={chartOptions} />
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Recent Bugs */}
      <Paper sx={{ p: 3, mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          Recent Bugs
        </Typography>
        {bugs.slice(0, 5).map((bug) => (
          <Box
            key={bug.id}
            sx={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              py: 1,
              borderBottom: '1px solid #eee',
            }}
          >
            <Typography variant="body1">{bug.title}</Typography>
            <Typography
              variant="body2"
              color={
                bug.priority === 'critical'
                  ? 'error'
                  : bug.priority === 'high'
                  ? 'warning.main'
                  : 'textSecondary'
              }
            >
              {bug.priority}
            </Typography>
          </Box>
        ))}
      </Paper>
    </Box>
  );
};

export default Dashboard;
