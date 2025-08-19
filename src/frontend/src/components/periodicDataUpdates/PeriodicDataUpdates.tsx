import { BaseSection } from '@components/core/BaseSection';
import { Box, Tab, Tabs, Fade } from '@mui/material';
import { ChangeEvent, ReactElement, useState } from 'react';
import { Link } from 'react-router-dom';
import AddIcon from '@mui/icons-material/Add';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { PeriodDataUpdatesUploadDialog } from './PeriodicDataUpdatesUploadDialog';
import { useProgramContext } from 'src/programContext';
import { usePermissions } from '@hooks/usePermissions';
import { hasPermissions, PERMISSIONS } from 'src/config/permissions';
import { ButtonTooltip } from '@components/core/ButtonTooltip';
import { PeriodicDataUpdatesOfflineTemplates } from './PeriodicDataUpdatesOfflineTemplates';
import { PeriodicDataUpdatesOfflineEdits } from './PeriodicDataUpdatesOfflineEdits';
import { PeriodicDataUpdatesOnlineEdits } from './PeriodicDataUpdatesOnlineEdits';

export const PeriodicDataUpdates = (): ReactElement => {
  const [value, setValue] = useState(0);
  const { baseUrl } = useBaseUrl();
  const { isSocialDctType } = useProgramContext();
  const permissions = usePermissions();

  const canCreatePDUTemplate = hasPermissions(
    PERMISSIONS.PDU_TEMPLATE_CREATE,
    permissions,
  );

  const handleChange = (_event: ChangeEvent<object>, newValue: number) => {
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
            <Tab label="Offline Templates" data-cy="pdu-offline-templates" />
            <Tab label="Offline Edits" data-cy="pdu-offline-edits" />
            <Tab label="Online Edits" data-cy="pdu-online-edits" />
          </Tabs>
        </Box>
      }
      buttons={null}
    >
      <Fade in={true} timeout={500} key={value}>
        <div>
          {value === 0 && (
            <Box>
              <Box display="flex" justifyContent="flex-end" mt={4}>
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
              <PeriodicDataUpdatesOfflineTemplates />
            </Box>
          )}
          {value === 1 && (
            <Box>
              <Box display="flex" justifyContent="flex-end" mt={4}>
                <PeriodDataUpdatesUploadDialog />
              </Box>
              <PeriodicDataUpdatesOfflineEdits />
            </Box>
          )}
          {value === 2 && (
            <Box>
              <PeriodicDataUpdatesOnlineEdits />
            </Box>
          )}
        </div>
      </Fade>
    </BaseSection>
  );
};
