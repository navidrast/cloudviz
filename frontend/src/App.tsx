import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';

import Layout from './components/layout/Layout';
import LoginComponent from './components/auth/LoginComponent';
import Dashboard from './components/dashboard/Dashboard';
import DiagramRenderer from './components/diagram/DiagramRenderer';
import ResourceFiltersComponent from './components/filters/ResourceFiltersComponent';
import { apiClient } from './services/api';
import { useValidateToken } from './hooks/api';
import { ResourceFilters } from './types/api';

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
    },
  },
});

// Create Material-UI theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1e3c72',
    },
    secondary: {
      main: '#2a5298',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 700,
    },
    h6: {
      fontWeight: 600,
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 600,
        },
      },
    },
  },
});

// Protected Route Component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isLoading, error } = useValidateToken();
  
  if (isLoading) {
    return <div>Loading...</div>;
  }
  
  if (error || !apiClient.isAuthenticated()) {
    return <LoginComponent onLoginSuccess={() => window.location.reload()} />;
  }
  
  return <Layout>{children}</Layout>;
};

// Placeholder components for routes
const ResourcesPage: React.FC = () => {
  const [filters, setFilters] = React.useState<ResourceFilters>({
    providers: [],
    resource_types: [],
    regions: [],
    tags: {},
    environments: [],
  });

  return (
    <div>
      <ResourceFiltersComponent
        filters={filters}
        onFiltersChange={setFilters}
        onApplyFilters={() => console.log('Apply filters:', filters)}
        onClearFilters={() => setFilters({
          providers: [],
          resource_types: [],
          regions: [],
          tags: {},
          environments: [],
        })}
      />
    </div>
  );
};

const DiagramsPage: React.FC = () => {
  return (
    <div>
      <DiagramRenderer
        title="Infrastructure Diagram"
        enableExport={true}
        enableFullscreen={true}
      />
    </div>
  );
};

const AnalyticsPage: React.FC = () => {
  return <div>Cost Analytics - Coming Soon</div>;
};

const CompliancePage: React.FC = () => {
  return <div>Security & Compliance - Coming Soon</div>;
};

const SettingsPage: React.FC = () => {
  return <div>Settings - Coming Soon</div>;
};

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <LocalizationProvider dateAdapter={AdapterDateFns}>
          <Router>
            <Routes>
              <Route path="/login" element={<LoginComponent />} />
              <Route path="/" element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              } />
              <Route path="/resources" element={
                <ProtectedRoute>
                  <ResourcesPage />
                </ProtectedRoute>
              } />
              <Route path="/diagrams" element={
                <ProtectedRoute>
                  <DiagramsPage />
                </ProtectedRoute>
              } />
              <Route path="/analytics" element={
                <ProtectedRoute>
                  <AnalyticsPage />
                </ProtectedRoute>
              } />
              <Route path="/compliance" element={
                <ProtectedRoute>
                  <CompliancePage />
                </ProtectedRoute>
              } />
              <Route path="/settings" element={
                <ProtectedRoute>
                  <SettingsPage />
                </ProtectedRoute>
              } />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </Router>
        </LocalizationProvider>
      </ThemeProvider>
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}

export default App;
