import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import {
  Box,
  Paper,
  Typography,
  Chip,
  Button,
  TextField,
  Grid,
  Divider,
  Avatar,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  ArrowBack as ArrowBackIcon,
  Send as SendIcon,
} from '@mui/icons-material';
import { useBugStore } from '../store/bugStore';
import { useAuthStore } from '../store/authStore';

const BugDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { currentBug, fetchBug, deleteBug, addComment, loading } = useBugStore();
  const { user } = useAuthStore();
  const [commentError, setCommentError] = useState('');

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm();

  useEffect(() => {
    if (id) {
      fetchBug(id);
    }
  }, [id, fetchBug]);

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this bug?')) {
      const result = await deleteBug(id);
      if (result.success) {
        navigate('/bugs');
      }
    }
  };

  const handleAddComment = async (data) => {
    setCommentError('');
    const result = await addComment(id, {
      content: data.comment,
      author: user.id,
    });

    if (result.success) {
      reset();
    } else {
      setCommentError(result.error || 'Failed to add comment');
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'critical':
        return 'error';
      case 'high':
        return 'warning';
      case 'medium':
        return 'info';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'open':
        return 'error';
      case 'in_progress':
        return 'warning';
      case 'resolved':
        return 'success';
      case 'closed':
        return 'default';
      default:
        return 'default';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (!currentBug) {
    return (
      <Box>
        <Alert severity="error">Bug not found</Alert>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/bugs')}
          sx={{ mr: 2 }}
        >
          Back to Bugs
        </Button>
        <Typography variant="h4" sx={{ flexGrow: 1 }}>
          Bug #{currentBug.id}
        </Typography>
        <Button
          variant="outlined"
          startIcon={<EditIcon />}
          onClick={() => navigate(`/bugs/${id}/edit`)}
          sx={{ mr: 1 }}
        >
          Edit
        </Button>
        <Button
          variant="outlined"
          color="error"
          startIcon={<DeleteIcon />}
          onClick={handleDelete}
        >
          Delete
        </Button>
      </Box>

      <Grid container spacing={3}>
        {/* Main Content */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h5" gutterBottom>
              {currentBug.title}
            </Typography>
            
            <Box sx={{ display: 'flex', gap: 1, mb: 3 }}>
              <Chip
                label={currentBug.priority}
                color={getPriorityColor(currentBug.priority)}
                size="small"
              />
              <Chip
                label={currentBug.status.replace('_', ' ')}
                color={getStatusColor(currentBug.status)}
                size="small"
              />
              {currentBug.tags?.map((tag) => (
                <Chip key={tag} label={tag} variant="outlined" size="small" />
              ))}
            </Box>

            <Typography variant="h6" gutterBottom>
              Description
            </Typography>
            <Typography variant="body1" paragraph>
              {currentBug.description}
            </Typography>

            {currentBug.steps_to_reproduce && (
              <>
                <Typography variant="h6" gutterBottom>
                  Steps to Reproduce
                </Typography>
                <Typography variant="body1" paragraph>
                  {currentBug.steps_to_reproduce}
                </Typography>
              </>
            )}

            {currentBug.expected_behavior && (
              <>
                <Typography variant="h6" gutterBottom>
                  Expected Behavior
                </Typography>
                <Typography variant="body1" paragraph>
                  {currentBug.expected_behavior}
                </Typography>
              </>
            )}
          </Paper>

          {/* Comments Section */}
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Comments ({currentBug.comments?.length || 0})
            </Typography>

            {/* Add Comment Form */}
            {commentError && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {commentError}
              </Alert>
            )}

            <Box component="form" onSubmit={handleSubmit(handleAddComment)} sx={{ mb: 3 }}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Add a comment..."
                {...register('comment', {
                  required: 'Comment is required',
                  minLength: {
                    value: 5,
                    message: 'Comment must be at least 5 characters',
                  },
                })}
                error={!!errors.comment}
                helperText={errors.comment?.message}
                sx={{ mb: 2 }}
              />
              <Button
                type="submit"
                variant="contained"
                startIcon={<SendIcon />}
                disabled={loading}
              >
                Add Comment
              </Button>
            </Box>

            <Divider sx={{ mb: 2 }} />

            {/* Comments List */}
            <List>
              {currentBug.comments?.map((comment, index) => (
                <ListItem key={index} alignItems="flex-start">
                  <ListItemAvatar>
                    <Avatar>
                      {comment.author?.username?.charAt(0).toUpperCase() || 'U'}
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="subtitle2">
                          {comment.author?.username || 'Unknown User'}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          {new Date(comment.created_at).toLocaleString()}
                        </Typography>
                      </Box>
                    }
                    secondary={
                      <Typography variant="body2" sx={{ mt: 1 }}>
                        {comment.content}
                      </Typography>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>

        {/* Sidebar */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Bug Details
            </Typography>
            
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="textSecondary">
                Reporter
              </Typography>
              <Typography variant="body1">
                {currentBug.reporter?.username || 'Unknown'}
              </Typography>
            </Box>

            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="textSecondary">
                Assignee
              </Typography>
              <Typography variant="body1">
                {currentBug.assignee?.username || 'Unassigned'}
              </Typography>
            </Box>

            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="textSecondary">
                Created
              </Typography>
              <Typography variant="body1">
                {new Date(currentBug.created_at).toLocaleDateString()}
              </Typography>
            </Box>

            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="textSecondary">
                Last Updated
              </Typography>
              <Typography variant="body1">
                {new Date(currentBug.updated_at).toLocaleDateString()}
              </Typography>
            </Box>

            {currentBug.environment && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="textSecondary">
                  Environment
                </Typography>
                <Typography variant="body1">
                  {currentBug.environment}
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default BugDetail;
