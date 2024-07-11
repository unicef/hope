import { BaseSection } from '@components/core/BaseSection';
import { Box, Tab, Tabs, Button, Fade } from '@mui/material';
import { useState } from 'react';
import { Link } from 'react-router-dom';
import AddIcon from '@mui/icons-material/Add';
import { PeriodicDataUpdatesTemplatesList } from './PeriodicDataUpdatesTemplatesList';
import { PeriodicDataUpdatesUpdatesList } from './PeriodicDataUpdatesUpdatesList';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { PeriodDataUpdatesUploadDialog } from './PeriodicDataUpdatesUploadDialog';

export const PeriodicDataUpdates = (): React.ReactElement => {
  const [value, setValue] = useState(0);
  const { baseUrl } = useBaseUrl();

  const handleChange = (
    _event: React.ChangeEvent<object>,
    newValue: number,
  ) => {
    setValue(newValue);
  };

  return (
    <BaseSection
      title="Periodic Data Updates"
      tabs={
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs
            value={value}
            onChange={handleChange}
            aria-label="periodic data updates tabs"
          >
            <Tab label="Templates" />
            <Tab label="Updates" />
          </Tabs>
        </Box>
      }
      buttons={
        <Box display="flex" align-items="center">
          <Box mr={2}>
            <Button
              variant="contained"
              color="primary"
              component={Link}
              to={`/${baseUrl}/population/household-members/new-template`}
              startIcon={<AddIcon />}
            >
              New Template
            </Button>
          </Box>
          <Box>
            <PeriodDataUpdatesUploadDialog />
          </Box>
        </Box>
      }
    >
      <Fade in={true} timeout={500} key={value}>
        {value === 0 ? (
          <Box>
            <PeriodicDataUpdatesTemplatesList />
          </Box>
        ) : (
          <Box>
            <PeriodicDataUpdatesUpdatesList />
          </Box>
        )}
      </Fade>
    </BaseSection>
  );
};
