import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  OutlinedInput,
  TextField,
  Button,
  Grid,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  IconButton,
  Tooltip,
  SelectChangeEvent,
} from '@mui/material';
import {
  ExpandMore,
  FilterList,
  Clear,
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { CloudProvider, ResourceFilters } from '../../types/api';
import { useProviders } from '../../hooks/api';

interface ResourceFiltersComponentProps {
  filters: ResourceFilters;
  onFiltersChange: (filters: ResourceFilters) => void;
  onApplyFilters: () => void;
  onClearFilters: () => void;
  loading?: boolean;
}

const MENU_PROPS = {
  PaperProps: {
    style: {
      maxHeight: 224,
      width: 250,
    },
  },
};

const ENVIRONMENTS = ['production', 'staging', 'development', 'testing', 'demo'];

const ResourceFiltersComponent: React.FC<ResourceFiltersComponentProps> = ({
  filters,
  onFiltersChange,
  onApplyFilters,
  onClearFilters,
  loading = false,
}) => {
  const { data: providersData } = useProviders();
  const [expanded, setExpanded] = useState<string | false>('basic');
  
  // Local state for tag input
  const [tagKey, setTagKey] = useState('');
  const [tagValue, setTagValue] = useState('');

  const handleAccordionChange = (panel: string) => (
    event: React.SyntheticEvent,
    isExpanded: boolean
  ) => {
    setExpanded(isExpanded ? panel : false);
  };

  const handleProviderChange = (event: SelectChangeEvent<CloudProvider[]>) => {
    const value = event.target.value;
    onFiltersChange({
      ...filters,
      providers: typeof value === 'string' ? [value as CloudProvider] : value as CloudProvider[],
    });
  };

  const handleResourceTypesChange = (event: SelectChangeEvent<string[]>) => {
    const value = event.target.value;
    onFiltersChange({
      ...filters,
      resource_types: typeof value === 'string' ? [value] : value,
    });
  };

  const handleRegionsChange = (event: SelectChangeEvent<string[]>) => {
    const value = event.target.value;
    onFiltersChange({
      ...filters,
      regions: typeof value === 'string' ? [value] : value,
    });
  };

  const handleEnvironmentsChange = (event: SelectChangeEvent<string[]>) => {
    const value = event.target.value;
    onFiltersChange({
      ...filters,
      environments: typeof value === 'string' ? [value] : value,
    });
  };

  const handleAddTag = () => {
    if (tagKey.trim() && tagValue.trim()) {
      onFiltersChange({
        ...filters,
        tags: {
          ...filters.tags,
          [tagKey.trim()]: tagValue.trim(),
        },
      });
      setTagKey('');
      setTagValue('');
    }
  };

  const handleRemoveTag = (key: string) => {
    const newTags = { ...filters.tags };
    delete newTags[key];
    onFiltersChange({
      ...filters,
      tags: newTags,
    });
  };

  const handleDateRangeChange = (field: 'start' | 'end') => (date: Date | null) => {
    const currentRange = filters.date_range || { start: '', end: '' };
    onFiltersChange({
      ...filters,
      date_range: {
        ...currentRange,
        [field]: date ? date.toISOString() : '',
      },
    });
  };

  // Get all available resource types from providers
  const getAllResourceTypes = () => {
    if (!providersData?.providers) return [];
    
    const resourceTypes = new Set<string>();
    providersData.providers.forEach(provider => {
      provider.supported_resource_types.forEach(type => resourceTypes.add(type));
    });
    
    return Array.from(resourceTypes).sort();
  };

  // Get all available regions from providers
  const getAllRegions = () => {
    if (!providersData?.providers) return [];
    
    const regions = new Set<string>();
    providersData.providers.forEach(provider => {
      provider.regions.forEach(region => regions.add(region));
    });
    
    return Array.from(regions).sort();
  };

  const hasActiveFilters = () => {
    return (
      filters.providers.length > 0 ||
      filters.resource_types.length > 0 ||
      filters.regions.length > 0 ||
      filters.environments.length > 0 ||
      Object.keys(filters.tags).length > 0 ||
      (filters.date_range?.start && filters.date_range?.end)
    );
  };

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <FilterList sx={{ mr: 1 }} />
            <Typography variant="h6" component="h2">
              Resource Filters
            </Typography>
            {hasActiveFilters() && (
              <Chip
                label={`${filters.providers.length + filters.resource_types.length + filters.regions.length + filters.environments.length + Object.keys(filters.tags).length} active`}
                size="small"
                color="primary"
                sx={{ ml: 1 }}
              />
            )}
          </Box>
          <Box>
            <Tooltip title="Clear All Filters">
              <IconButton onClick={onClearFilters} disabled={!hasActiveFilters()}>
                <Clear />
              </IconButton>
            </Tooltip>
            <Button
              variant="contained"
              onClick={onApplyFilters}
              disabled={loading}
              sx={{ ml: 1 }}
            >
              Apply Filters
            </Button>
          </Box>
        </Box>

        {/* Basic Filters */}
        <Accordion 
          expanded={expanded === 'basic'} 
          onChange={handleAccordionChange('basic')}
        >
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Typography variant="subtitle1">Basic Filters</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={2}>
              {/* Cloud Providers */}
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Cloud Providers</InputLabel>
                  <Select
                    multiple
                    value={filters.providers}
                    onChange={handleProviderChange}
                    input={<OutlinedInput label="Cloud Providers" />}
                    renderValue={(selected) => (
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                        {selected.map((value) => (
                          <Chip 
                            key={value} 
                            label={value.toUpperCase()} 
                            size="small"
                            onDelete={() => {
                              onFiltersChange({
                                ...filters,
                                providers: filters.providers.filter(p => p !== value),
                              });
                            }}
                          />
                        ))}
                      </Box>
                    )}
                    MenuProps={MENU_PROPS}
                  >
                    {Object.values(CloudProvider).map((provider) => (
                      <MenuItem key={provider} value={provider}>
                        {provider.toUpperCase()}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              {/* Environments */}
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Environments</InputLabel>
                  <Select
                    multiple
                    value={filters.environments}
                    onChange={handleEnvironmentsChange}
                    input={<OutlinedInput label="Environments" />}
                    renderValue={(selected) => (
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                        {selected.map((value) => (
                          <Chip 
                            key={value} 
                            label={value} 
                            size="small"
                            onDelete={() => {
                              onFiltersChange({
                                ...filters,
                                environments: filters.environments.filter(e => e !== value),
                              });
                            }}
                          />
                        ))}
                      </Box>
                    )}
                    MenuProps={MENU_PROPS}
                  >
                    {ENVIRONMENTS.map((env) => (
                      <MenuItem key={env} value={env}>
                        {env}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </AccordionDetails>
        </Accordion>

        {/* Advanced Filters */}
        <Accordion 
          expanded={expanded === 'advanced'} 
          onChange={handleAccordionChange('advanced')}
        >
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Typography variant="subtitle1">Advanced Filters</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={2}>
              {/* Resource Types */}
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Resource Types</InputLabel>
                  <Select
                    multiple
                    value={filters.resource_types}
                    onChange={handleResourceTypesChange}
                    input={<OutlinedInput label="Resource Types" />}
                    renderValue={(selected) => (
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                        {selected.map((value) => (
                          <Chip 
                            key={value} 
                            label={value} 
                            size="small"
                            onDelete={() => {
                              onFiltersChange({
                                ...filters,
                                resource_types: filters.resource_types.filter(r => r !== value),
                              });
                            }}
                          />
                        ))}
                      </Box>
                    )}
                    MenuProps={MENU_PROPS}
                  >
                    {getAllResourceTypes().map((type) => (
                      <MenuItem key={type} value={type}>
                        {type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              {/* Regions */}
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Regions</InputLabel>
                  <Select
                    multiple
                    value={filters.regions}
                    onChange={handleRegionsChange}
                    input={<OutlinedInput label="Regions" />}
                    renderValue={(selected) => (
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                        {selected.map((value) => (
                          <Chip 
                            key={value} 
                            label={value} 
                            size="small"
                            onDelete={() => {
                              onFiltersChange({
                                ...filters,
                                regions: filters.regions.filter(r => r !== value),
                              });
                            }}
                          />
                        ))}
                      </Box>
                    )}
                    MenuProps={MENU_PROPS}
                  >
                    {getAllRegions().map((region) => (
                      <MenuItem key={region} value={region}>
                        {region}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </AccordionDetails>
        </Accordion>

        {/* Tags and Date Range */}
        <Accordion 
          expanded={expanded === 'tags'} 
          onChange={handleAccordionChange('tags')}
        >
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Typography variant="subtitle1">
              Tags & Date Range
              {Object.keys(filters.tags).length > 0 && (
                <Chip
                  label={`${Object.keys(filters.tags).length} tags`}
                  size="small"
                  sx={{ ml: 1 }}
                />
              )}
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={2}>
              {/* Tags Input */}
              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom>
                  Resource Tags
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                  <TextField
                    size="small"
                    label="Tag Key"
                    value={tagKey}
                    onChange={(e) => setTagKey(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleAddTag()}
                  />
                  <TextField
                    size="small"
                    label="Tag Value"
                    value={tagValue}
                    onChange={(e) => setTagValue(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleAddTag()}
                  />
                  <Button
                    variant="outlined"
                    onClick={handleAddTag}
                    disabled={!tagKey.trim() || !tagValue.trim()}
                  >
                    Add
                  </Button>
                </Box>
                
                {/* Active Tags */}
                {Object.keys(filters.tags).length > 0 && (
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {Object.entries(filters.tags).map(([key, value]) => (
                      <Chip
                        key={key}
                        label={`${key}: ${value}`}
                        onDelete={() => handleRemoveTag(key)}
                        variant="outlined"
                      />
                    ))}
                  </Box>
                )}
              </Grid>

              {/* Date Range */}
              <Grid item xs={12}>
                <Typography variant="subtitle2" gutterBottom>
                  Date Range
                </Typography>
                <LocalizationProvider dateAdapter={AdapterDateFns}>
                  <Box sx={{ display: 'flex', gap: 2 }}>
                    <DatePicker
                      label="Start Date"
                      value={filters.date_range?.start ? new Date(filters.date_range.start) : null}
                      onChange={handleDateRangeChange('start')}
                      slotProps={{ textField: { size: 'small' } }}
                    />
                    <DatePicker
                      label="End Date"
                      value={filters.date_range?.end ? new Date(filters.date_range.end) : null}
                      onChange={handleDateRangeChange('end')}
                      slotProps={{ textField: { size: 'small' } }}
                    />
                  </Box>
                </LocalizationProvider>
              </Grid>
            </Grid>
          </AccordionDetails>
        </Accordion>
      </CardContent>
    </Card>
  );
};

export default ResourceFiltersComponent;