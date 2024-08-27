import { BaseSection } from '@components/core/BaseSection';
import { Box, Tab, Tabs, Button, Fade } from '@mui/material';
import { useState } from 'react';
import { Link } from 'react-router-dom';
import AddIcon from '@mui/icons-material/Add';
import { PeriodicDataUpdatesTemplatesList } from './PeriodicDataUpdatesTemplatesList';
import { PeriodicDataUpdatesUpdatesList } from './PeriodicDataUpdatesUpdatesList';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { PeriodDataUpdatesUploadDialog } from './PeriodicDataUpdatesUploadDialog';
import { useProgramContext } from 'src/programContext';
import { usePermissions } from '@hooks/usePermissions';
import { hasPermissions, PERMISSIONS } from 'src/config/permissions';
import { ButtonTooltip } from '@components/core/ButtonTooltip';

export const PeriodicDataUpdates = (): React.ReactElement => {
  const [value, setValue] = useState(0);
  const { baseUrl } = useBaseUrl();
  const { isSocialDctType } = useProgramContext();
  const permissions = usePermissions();

  const canCreatePDUTemplate = hasPermissions(
    PERMISSIONS.PDU_TEMPLATE_CREATE,
    permissions,
  );

  const handleChange = (
    _event: React.ChangeEvent<object>,
    newValue: number,
  ) => {
    setValue(newValue);
  };

  const newTemplatePath = isSocialDctType
    ? `/${baseUrl}/population/people/new-template`
    : `/${baseUrl}/population/individuals/new-template`;

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
            <Tab label="Templates" data-cy="pdu-templates" />
            <Tab label="Updates" data-cy="pdu-updates" />
          </Tabs>
        </Box>
      }
      buttons={
        <Box display="flex" align-items="center">
          <Box mr={2}>
            <ButtonTooltip
              variant="contained"
              color="primary"
              component={Link}
              to={newTemplatePath}
              startIcon={<AddIcon />}
              data-cy="new-template-button"
              disabled={!canCreatePDUTemplate}
            >
              New Template
            </ButtonTooltip>
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
