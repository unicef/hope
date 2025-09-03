import { BaseSection } from '@components/core/BaseSection';
import { Box, Tab, Tabs, Fade, Paper } from '@mui/material';
import { ChangeEvent, ReactElement, useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import AddIcon from '@mui/icons-material/Add';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { PeriodDataUpdatesUploadDialog } from './PeriodicDataUpdatesUploadDialog';
import { useProgramContext } from 'src/programContext';
import { usePermissions } from '@hooks/usePermissions';
import { hasPermissions, PERMISSIONS } from 'src/config/permissions';
import { ButtonTooltip } from '@components/core/ButtonTooltip';
import { PeriodicDataUpdatesOfflineTemplates } from './PeriodicDataUpdatesOfflineTemplates';
import { PeriodicDataUpdatesOfflineEdits } from './PeriodicDataUpdatesOfflineEdits';
import PeriodicDataUpdatesOnlineEdits from './PeriodicDataUpdatesOnlineEdits';
export const PeriodicDataUpdates = (): ReactElement => {
  const location = useLocation();
  const navigate = useNavigate();
  // Nested tab logic: tab=periodic-data-updates&subtab=offline-templates
  const searchParams = new URLSearchParams(location.search);
  const subtabParam = searchParams.get('subtab');
  const initialTab =
    subtabParam === 'offline-edits'
      ? 1
      : subtabParam === 'online-edits'
        ? 2
        : 0;
  const [value, setValue] = useState(initialTab);

  useEffect(() => {
    const subtabParamEffect = new URLSearchParams(location.search).get(
      'subtab',
    );
    if (subtabParamEffect === 'offline-edits' && value !== 1) {
      setValue(1);
    } else if (subtabParamEffect === 'online-edits' && value !== 2) {
      setValue(2);
    } else if (
      (subtabParamEffect === 'offline-templates' || !subtabParamEffect) &&
      value !== 0
    ) {
      setValue(0);
    }
  }, [location.search, value]);
  const { baseUrl } = useBaseUrl();
  const { isSocialDctType } = useProgramContext();
  const permissions = usePermissions();

  const canCreatePDUTemplate = hasPermissions(
    PERMISSIONS.PDU_TEMPLATE_CREATE,
    permissions,
  );

  const handleChange = (_event: ChangeEvent<object>, newValue: number) => {
    setValue(newValue);
    const tabParam = searchParams.get('tab') || 'periodic-data-updates';
    let subtab = 'offline-templates';
    if (newValue === 1) subtab = 'offline-edits';
    if (newValue === 2) subtab = 'online-edits';
    navigate(
      { search: `?tab=${tabParam}&subtab=${subtab}` },
      { replace: true },
    );
  };

  const newTemplatePath = isSocialDctType
    ? `/${baseUrl}/population/people/new-offline-template`
    : `/${baseUrl}/population/individuals/new-offline-template`;

  return (
    <>
      <Box p={3}>
        <Paper elevation={1} sx={{ mb: 0, borderRadius: 2 }}>
          <BaseSection
            title="Periodic Data Updates"
            tabs={
              <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                <Tabs
                  value={value}
                  onChange={handleChange}
                  aria-label="periodic data updates tabs"
                >
                  <Tab
                    label="Offline Templates"
                    data-cy="pdu-offline-templates"
                  />
                  <Tab label="Offline Edits" data-cy="pdu-offline-edits" />
                  <Tab label="Online Edits" data-cy="pdu-online-edits" />
                </Tabs>
              </Box>
            }
          />
        </Paper>
      </Box>
      <Fade in={true} timeout={500} key={value}>
        <div>
          {value === 0 && (
            <Box p={3}>
              <Paper>
                <Box display="flex" justifyContent="flex-end" p={6}>
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
              </Paper>
            </Box>
          )}
          {value === 1 && (
            <Box p={3}>
              <Paper>
                <Box display="flex" justifyContent="flex-end" p={6}>
                  <PeriodDataUpdatesUploadDialog />
                </Box>
                <PeriodicDataUpdatesOfflineEdits />
              </Paper>
            </Box>
          )}
          {value === 2 && (
            <Box>
              <PeriodicDataUpdatesOnlineEdits />
            </Box>
          )}
        </div>
      </Fade>
    </>
  );
};
