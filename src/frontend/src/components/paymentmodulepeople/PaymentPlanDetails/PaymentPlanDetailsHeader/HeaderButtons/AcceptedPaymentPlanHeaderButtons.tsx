import React, { useState } from 'react';
import {
  Box,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Button,
  Select,
  MenuItem,
} from '@mui/material';
import LoadingButton from '@mui/lab/LoadingButton';
import GetApp from '@mui/icons-material/GetApp';
import { Action } from '@generated/graphql';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { CreateFollowUpPaymentPlan } from '@components/paymentmodule/CreateFollowUpPaymentPlan';
import { SplitIntoPaymentLists } from '../SplitIntoPaymentLists';
import { useTranslation } from 'react-i18next';
import { usePermissions } from '@hooks/usePermissions';
import { hasPermissions, PERMISSIONS } from 'src/config/permissions';
import { usePaymentPlanAction } from '@hooks/usePaymentPlanAction';

export const AcceptedPaymentPlanHeaderButtons = ({
  loadingExport,
  isDisabledExportXlsx,
  hasDownloadMtcnPermission,
  mutateExport,
  paymentPlan,
  showMessage,
}) => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const permissions = usePermissions();
  const { data, loading } = useAllFinancialServiceProviderXlsxTemplatesQuery();
  const { mutatePaymentPlanAction: sendXlsxPassword, loading: loadingSend } =
    usePaymentPlanAction(Action.SendXlsxPassword, paymentPlan.id, () =>
      showMessage(t('Password has been sent.')),
    );
  const canSplit = hasPermissions(permissions, [PERMISSIONS.PM_SPLIT]);
  if (loading) return <LoadingComponent />;
  if (!data) return null;

  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const handleTemplateChange = (event) => {
    setSelectedTemplate(event.target.value);
  };

  const handleExport = async () => {
    try {
      await mutateExport({
        variables: {
          paymentPlanId: paymentPlan.id,
          template: selectedTemplate,
        },
      });
      showMessage(t('Exporting XLSX started'));
      handleClose();
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  return (
    <Box display="flex" alignItems="center">
      <>
        {paymentPlan.canCreateFollowUp && (
          <Box p={2}>
            <CreateFollowUpPaymentPlan paymentPlan={paymentPlan} />
          </Box>
        )}
        <Box p={2}>
          <SplitIntoPaymentLists
            paymentPlan={paymentPlan}
            canSplit={canSplit}
          />
        </Box>
        <Box m={2}>
          {!paymentPlan.hasPaymentListExportFile && (
            <LoadingButton
              loading={loadingExport}
              disabled={isDisabledExportXlsx || !hasDownloadMtcnPermission}
              color="primary"
              variant="contained"
              startIcon={<GetApp />}
              data-cy="button-export-xlsx"
              onClick={handleClickOpen}
            >
              {t('Export Xlsx')}
            </LoadingButton>
          )}
          <Dialog open={open} onClose={handleClose}>
            <DialogTitle>{t('Select Template')}</DialogTitle>
            <DialogContent>
              <Select
                value={selectedTemplate}
                onChange={handleTemplateChange}
                fullWidth
                variant="outlined"
                size="small"
                data-cy="select-template"
              >
                {data.allFinancialServiceProviderXlsxTemplates.edges.map(
                  ({ node }) => (
                    <MenuItem key={node.id} value={node.id}>
                      {node.name}
                    </MenuItem>
                  ),
                )}
              </Select>
            </DialogContent>
            <DialogActions>
              <Button
                data-cy="cancel-button"
                onClick={handleClose}
                color="primary"
              >
                {t('Cancel')}
              </Button>
              <Button
                onClick={handleExport}
                data-cy="export-button"
                color="primary"
                disabled={!selectedTemplate}
              >
                {t('Export Xlsx')}
              </Button>
            </DialogActions>
          </Dialog>
        </Box>
        <Box m={2}>
          <LoadingButton
            loading={loadingSend}
            disabled={loadingSend}
            color="primary"
            variant="contained"
            data-cy="button-send-xlsx-password"
            onClick={() => sendXlsxPassword()}
          >
            {t('Send Xlsx Password')}
          </LoadingButton>
        </Box>
      </>
    </Box>
  );
};
