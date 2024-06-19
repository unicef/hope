import { BaseSection } from '@components/core/BaseSection';
import { Box, Tab, Tabs } from '@mui/material';
import { useState } from 'react';

export const PeriodicDataUpdates = (): React.ReactElement => {
  const [value, setValue] = useState(0);

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
            aria-label="basic tabs example"
          >
            <Tab label="Templates" />
            <Tab label="Updates" />
          </Tabs>
        </Box>
      }
    >
      {value === 0 && <Box>Templates Content</Box>}
      {value === 1 && <Box>Updates Content</Box>}
    </BaseSection>
  );
};
