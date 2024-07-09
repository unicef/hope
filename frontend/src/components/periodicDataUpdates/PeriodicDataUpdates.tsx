import { BaseSection } from '@components/core/BaseSection';
import { Box, Tab, Tabs, Button } from '@mui/material';
import { useState } from 'react';
import { Link } from 'react-router-dom';
import AddIcon from '@mui/icons-material/Add';
import UploadIcon from '@mui/icons-material/Upload';
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

  //TODO MS: add correct paths for the tabs and button
  return (
    <BaseSection
      title="Periodic Data Updates"
      tabs={
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs
            value={value}
            onChange={handleChange}
            aria-label="basic tabs example"
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
      {value === 0 && (
        <Box>
          <PeriodicDataUpdatesTemplatesList />
        </Box>
      )}
      {value === 1 && (
        <Box>
          <PeriodicDataUpdatesUpdatesList />
        </Box>
      )}
    </BaseSection>
  );
};
