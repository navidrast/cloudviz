import React from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  CircularProgress,
  Alert,
  Avatar,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Cloud as CloudIcon,
  AttachMoney as CostIcon,
  Security as SecurityIcon,
  Assessment as AssessmentIcon,
  Refresh as RefreshIcon,
  CloudQueue,
  Storage,
  Computer,
  NetworkCheck,
} from '@mui/icons-material';
import { useCostSummary, useProviders } from '../../hooks/api';
import { CloudProvider } from '../../types/api';

const Dashboard: React.FC = () => {
  const { data: costData, isLoading: costLoading, error: costError, refetch: refetchCost } = useCostSummary();
  const { data: providersData, isLoading: providersLoading, error: providersError } = useProviders();

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const getProviderIcon = (provider: CloudProvider) => {
    switch (provider) {
      case CloudProvider.AZURE:
        return <CloudIcon sx={{ color: '#0078d4' }} />;
      case CloudProvider.AWS:
        return <CloudIcon sx={{ color: '#ff9900' }} />;
      case CloudProvider.GCP:
        return <CloudIcon sx={{ color: '#4285f4' }} />;
      default:
        return <CloudIcon />;
    }
  };

  const getProviderColor = (provider: CloudProvider) => {
    switch (provider) {
      case CloudProvider.AZURE:
        return '#0078d4';
      case CloudProvider.AWS:
        return '#ff9900';
      case CloudProvider.GCP:
        return '#4285f4';
      default:
        return '#757575';
    }
  };

  const StatCard: React.FC<{
    title: string;
    value: string | number;
    icon: React.ReactNode;
    color?: string;
    subtitle?: string;
    loading?: boolean;
    error?: any;
    onRefresh?: () => void;
  }> = ({ title, value, icon, color = 'primary.main', subtitle, loading, error, onRefresh }) => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Avatar sx={{ backgroundColor: color, marginRight: 2 }}>
              {icon}
            </Avatar>
            <Box>
              <Typography color="textSecondary" gutterBottom variant="overline">
                {title}
              </Typography>
              {loading ? (
                <CircularProgress size={24} />
              ) : error ? (
                <Typography variant="h6" color="error">
                  Error
                </Typography>
              ) : (
                <Typography variant="h4" component="div" fontWeight="bold">
                  {value}
                </Typography>
              )}
              {subtitle && (
                <Typography variant="body2" color="textSecondary">
                  {subtitle}
                </Typography>
              )}
            </Box>
          </Box>
          {onRefresh && (
            <Tooltip title="Refresh">
              <IconButton onClick={() => onRefresh()} size="small">
                <RefreshIcon />
              </IconButton>
            </Tooltip>
          )}
        </Box>
        {error && (
          <Alert severity="error" sx={{ mt: 1 }}>
            {(error as any)?.detail || 'Failed to load data'}
          </Alert>
        )}
      </CardContent>
    </Card>
  );

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
        Dashboard
      </Typography>
      <Typography variant="body1" color="textSecondary" paragraph>
        Overview of your multi-cloud infrastructure
      </Typography>

      <Grid container spacing={3}>
        {/* Cost Summary */}
        <Grid item xs={12} md={3}>
          <StatCard
            title="Total Monthly Cost"
            value={costData?.total_monthly_cost ? formatCurrency(costData.total_monthly_cost) : '$0.00'}
            icon={<CostIcon />}
            color="#4caf50"
            loading={costLoading}
            error={costError}
            onRefresh={refetchCost}
          />
        </Grid>

        {/* Total Resources */}
        <Grid item xs={12} md={3}>
          <StatCard
            title="Total Resources"
            value={
              costData?.providers
                ? Object.values(costData.providers).reduce((acc, provider) => acc + provider.resources, 0)
                : 0
            }
            icon={<CloudQueue />}
            color="#2196f3"
            loading={costLoading}
            error={costError}
          />
        </Grid>

        {/* Active Providers */}
        <Grid item xs={12} md={3}>
          <StatCard
            title="Active Providers"
            value={
              providersData?.providers
                ? providersData.providers.filter(p => p.configured).length
                : 0
            }
            icon={<CloudIcon />}
            color="#ff9800"
            loading={providersLoading}
            error={providersError}
          />
        </Grid>

        {/* Security Score */}
        <Grid item xs={12} md={3}>
          <StatCard
            title="Security Score"
            value="89%"
            icon={<SecurityIcon />}
            color="#9c27b0"
            subtitle="Good"
          />
        </Grid>

        {/* Provider Cost Breakdown */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h6" component="h2">
                  Cost by Cloud Provider
                </Typography>
                <Tooltip title="Refresh Cost Data">
                  <IconButton onClick={() => refetchCost()} size="small">
                    <RefreshIcon />
                  </IconButton>
                </Tooltip>
              </Box>

              {costLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                  <CircularProgress />
                </Box>
              ) : costError ? (
                <Alert severity="error">
                  Failed to load cost data: {(costError as any)?.detail}
                </Alert>
              ) : costData?.providers ? (
                <Grid container spacing={2}>
                  {Object.entries(costData.providers).map(([provider, data]) => (
                    <Grid item xs={12} sm={4} key={provider}>
                      <Card variant="outlined">
                        <CardContent>
                          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                            {getProviderIcon(provider as CloudProvider)}
                            <Typography variant="h6" sx={{ ml: 1, textTransform: 'uppercase' }}>
                              {provider}
                            </Typography>
                          </Box>
                          <Typography variant="h5" fontWeight="bold" color={getProviderColor(provider as CloudProvider)}>
                            {formatCurrency(data.cost)}
                          </Typography>
                          <Typography variant="body2" color="textSecondary">
                            {data.resources} resources • {data.regions} regions
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              ) : (
                <Typography variant="body2" color="textSecondary">
                  No cost data available
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Service Categories */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" component="h2" gutterBottom>
                Cost by Service Category
              </Typography>

              {costLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
                  <CircularProgress size={32} />
                </Box>
              ) : costData?.cost_breakdown ? (
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {Object.entries(costData.cost_breakdown).map(([category, cost]) => (
                    <Box key={category} sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        {category === 'compute' && <Computer sx={{ mr: 1, fontSize: 20 }} />}
                        {category === 'storage' && <Storage sx={{ mr: 1, fontSize: 20 }} />}
                        {category === 'networking' && <NetworkCheck sx={{ mr: 1, fontSize: 20 }} />}
                        {category === 'databases' && <AssessmentIcon sx={{ mr: 1, fontSize: 20 }} />}
                        <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                          {category}
                        </Typography>
                      </Box>
                      <Typography variant="body2" fontWeight="bold">
                        {formatCurrency(cost)}
                      </Typography>
                    </Box>
                  ))}
                </Box>
              ) : (
                <Typography variant="body2" color="textSecondary">
                  No service cost data available
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Cloud Providers Status */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" component="h2" gutterBottom>
                Cloud Provider Configuration
              </Typography>

              {providersLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
                  <CircularProgress />
                </Box>
              ) : providersError ? (
                <Alert severity="error">
                  Failed to load provider data: {(providersError as any)?.detail}
                </Alert>
              ) : providersData?.providers ? (
                <Grid container spacing={2}>
                  {providersData.providers.map((provider) => (
                    <Grid item xs={12} md={4} key={provider.name}>
                      <Card variant="outlined">
                        <CardContent>
                          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                              {getProviderIcon(provider.name)}
                              <Typography variant="h6" sx={{ ml: 1 }}>
                                {provider.display_name}
                              </Typography>
                            </Box>
                            <Chip
                              label={provider.configured ? 'Configured' : 'Not Configured'}
                              color={provider.configured ? 'success' : 'default'}
                              size="small"
                            />
                          </Box>
                          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 1 }}>
                            {provider.features.map((feature) => (
                              <Chip
                                key={feature}
                                label={feature}
                                size="small"
                                variant="outlined"
                              />
                            ))}
                          </Box>
                          <Typography variant="body2" color="textSecondary">
                            {provider.supported_resource_types.length} resource types supported
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              ) : (
                <Typography variant="body2" color="textSecondary">
                  No provider data available
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;