import { BaseSection } from '@components/core/BaseSection';
import { Box, Tab, Tabs, Button } from '@mui/material';
import { useState } from 'react';
import { Link } from 'react-router-dom';
import AddIcon from '@mui/icons-material/Add';
import UploadIcon from '@mui/icons-material/Upload';
import { PeriodicDataUpdatesTemplatesList } from './PeriodicDataUpdatesTemplatesList';
import { PeriodicDataUpdatesUpdatesList } from './PeriodicDataUpdatesUpdatesList';

export const PeriodicDataUpdates = (): React.ReactElement => {
  const [value, setValue] = useState(0);

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
        <>
          <Button
            variant="contained"
            color="primary"
            component={Link}
            to="/new-template"
            startIcon={<AddIcon />}
          >
            New Template
          </Button>
          <Button
            variant="contained"
            color="secondary"
            component={Link}
            to="/upload-data"
            endIcon={<UploadIcon />}
          >
            Upload Data
          </Button>
        </>
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
