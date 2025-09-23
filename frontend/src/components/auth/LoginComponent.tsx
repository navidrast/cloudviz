import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Container,
  Paper,
} from '@mui/material';
import { Cloud, Lock } from '@mui/icons-material';
import { useLogin } from '../../hooks/api';
import { LoginRequest } from '../../types/api';

interface LoginComponentProps {
  onLoginSuccess?: () => void;
}

const LoginComponent: React.FC<LoginComponentProps> = ({ onLoginSuccess }) => {
  const [credentials, setCredentials] = useState<LoginRequest>({
    username: '',
    password: '',
  });
  const [showError, setShowError] = useState(false);

  const loginMutation = useLogin();

  const handleInputChange = (field: keyof LoginRequest) => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setCredentials(prev => ({
      ...prev,
      [field]: event.target.value,
    }));
    if (showError) setShowError(false);
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    
    if (!credentials.username || !credentials.password) {
      setShowError(true);
      return;
    }

    try {
      await loginMutation.mutateAsync(credentials);
      onLoginSuccess?.();
    } catch (error) {
      setShowError(true);
    }
  };

  return (
    <Container component="main" maxWidth="sm">
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          background: 'linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)',
        }}
      >
        <Paper
          elevation={24}
          sx={{
            padding: 4,
            borderRadius: 3,
            width: '100%',
            maxWidth: 400,
          }}
        >
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              marginBottom: 3,
            }}
          >
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                marginBottom: 2,
              }}
            >
              <Cloud
                sx={{
                  fontSize: 40,
                  color: 'primary.main',
                  marginRight: 1,
                }}
              />
              <Typography
                variant="h4"
                component="h1"
                fontWeight="bold"
                color="primary"
              >
                CloudViz
              </Typography>
            </Box>
            <Typography variant="body1" color="text.secondary" textAlign="center">
              Multi-Cloud Infrastructure Visualization Platform
            </Typography>
          </Box>

          <Card variant="outlined">
            <CardContent>
              <Box
                component="form"
                onSubmit={handleSubmit}
                sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', marginBottom: 1 }}>
                  <Lock sx={{ marginRight: 1, color: 'text.secondary' }} />
                  <Typography variant="h6" component="h2">
                    Sign In
                  </Typography>
                </Box>

                {showError && (
                  <Alert severity="error">
                    {(loginMutation.error as any)?.detail || 'Invalid username or password'}
                  </Alert>
                )}

                <TextField
                  required
                  fullWidth
                  id="username"
                  label="Username"
                  name="username"
                  autoComplete="username"
                  autoFocus
                  value={credentials.username}
                  onChange={handleInputChange('username')}
                  error={showError && !credentials.username}
                  helperText={showError && !credentials.username ? 'Username is required' : ''}
                />

                <TextField
                  required
                  fullWidth
                  name="password"
                  label="Password"
                  type="password"
                  id="password"
                  autoComplete="current-password"
                  value={credentials.password}
                  onChange={handleInputChange('password')}
                  error={showError && !credentials.password}
                  helperText={showError && !credentials.password ? 'Password is required' : ''}
                />

                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  size="large"
                  disabled={loginMutation.isPending}
                  sx={{ mt: 2, mb: 2, height: 48 }}
                >
                  {loginMutation.isPending ? (
                    <CircularProgress size={24} />
                  ) : (
                    'Sign In'
                  )}
                </Button>

                <Typography variant="body2" color="text.secondary" textAlign="center">
                  Demo credentials: admin / admin
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Paper>
      </Box>
    </Container>
  );
};

export default LoginComponent;