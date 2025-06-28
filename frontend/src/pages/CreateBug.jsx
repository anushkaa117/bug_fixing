import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  Alert,
  CircularProgress,
} from '@mui/material';
import { Save as SaveIcon, Cancel as CancelIcon } from '@mui/icons-material';
import { useBugStore } from '../store/bugStore';

const CreateBug = () => {
  const navigate = useNavigate();
  const { createBug, loading } = useBugStore();
  const [submitError, setSubmitError] = useState('');

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm({
    defaultValues: {
      title: '',
      description: '',
      priority: 'medium',
      status: 'open',
      assignee: '',
      tags: '',
    },
  });

  const onSubmit = async (data) => {
    setSubmitError('');
    
    // Convert tags string to array
    const formattedData = {
      ...data,
      tags: data.tags ? data.tags.split(',').map(tag => tag.trim()) : [],
    };

    const result = await createBug(formattedData);
    
    if (result.success) {
      navigate('/bugs');
    } else {
      setSubmitError(result.error || 'Failed to create bug');
    }
  };

  const handleCancel = () => {
    navigate('/bugs');
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Create New Bug
      </Typography>

      <Paper sx={{ p: 4, maxWidth: 800 }}>
        {submitError && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {submitError}
          </Alert>
        )}

        <Box component="form" onSubmit={handleSubmit(onSubmit)}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Bug Title"
                {...register('title', {
                  required: 'Title is required',
                  minLength: {
                    value: 5,
                    message: 'Title must be at least 5 characters',
                  },
                })}
                error={!!errors.title}
                helperText={errors.title?.message}
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={6}
                label="Description"
                {...register('description', {
                  required: 'Description is required',
                  minLength: {
                    value: 10,
                    message: 'Description must be at least 10 characters',
                  },
                })}
                error={!!errors.description}
                helperText={errors.description?.message}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Priority</InputLabel>
                <Select
                  label="Priority"
                  {...register('priority', { required: 'Priority is required' })}
                  defaultValue="medium"
                  error={!!errors.priority}
                >
                  <MenuItem value="low">Low</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="high">High</MenuItem>
                  <MenuItem value="critical">Critical</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  label="Status"
                  {...register('status', { required: 'Status is required' })}
                  defaultValue="open"
                  error={!!errors.status}
                >
                  <MenuItem value="open">Open</MenuItem>
                  <MenuItem value="in_progress">In Progress</MenuItem>
                  <MenuItem value="resolved">Resolved</MenuItem>
                  <MenuItem value="closed">Closed</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Assignee (Username)"
                {...register('assignee')}
                helperText="Leave empty for unassigned"
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Tags"
                {...register('tags')}
                helperText="Comma-separated tags (e.g., frontend, critical, ui)"
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Steps to Reproduce"
                multiline
                rows={4}
                {...register('steps_to_reproduce')}
                helperText="Optional: Steps to reproduce the bug"
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Expected Behavior"
                multiline
                rows={3}
                {...register('expected_behavior')}
                helperText="Optional: What should happen instead"
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Environment"
                {...register('environment')}
                helperText="Optional: Browser, OS, version, etc."
              />
            </Grid>

            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                <Button
                  variant="outlined"
                  startIcon={<CancelIcon />}
                  onClick={handleCancel}
                  disabled={loading}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant="contained"
                  startIcon={loading ? <CircularProgress size={20} /> : <SaveIcon />}
                  disabled={loading}
                >
                  {loading ? 'Creating...' : 'Create Bug'}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </Box>
      </Paper>
    </Box>
  );
};

export default CreateBug;
