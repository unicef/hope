import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  MenuItem,
  Select,
} from '@mui/material';
import { GetApp } from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { useSnackbar } from '@hooks/useSnackBar';
import { LoadingButton } from '../../../../core/LoadingButton';
import { CreateFollowUpPaymentPlan } from '../../../CreateFollowUpPaymentPlan';
import { usePaymentPlanAction } from '../../../../../hooks/usePaymentPlanAction';
import {
  Action,
  PaymentPlanBackgroundActionStatus,
  useAllFinancialServiceProviderXlsxTemplatesQuery,
  useExportXlsxPpListPerFspMutation,
} from '../../../../../__generated__/graphql';
import { SplitIntoPaymentLists } from '../SplitIntoPaymentLists';
import { ReactElement, useState } from 'react';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';

export interface AcceptedPaymentPlanHeaderButtonsProps {
  canSendToPaymentGateway: boolean;
  canSplit: boolean;
  paymentPlan: PaymentPlanDetail;
}

export function AcceptedPaymentPlanHeaderButtons({
  canSendToPaymentGateway,
  canSplit,
  paymentPlan,
}: AcceptedPaymentPlanHeaderButtonsProps): ReactElement {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const { showMessage } = useSnackbar();
  const { data, loading } = useAllFinancialServiceProviderXlsxTemplatesQuery();
  const { mutatePaymentPlanAction: sendXlsxPassword, loading: loadingSend } =
    usePaymentPlanAction(Action.SendXlsxPassword, paymentPlan.id, () =>
      showMessage(t('Password has been sent.')),
    );

  const [mutateExport, { loading: loadingExport }] =
    useExportXlsxPpListPerFspMutation();

  const {
    mutatePaymentPlanAction: sendToPaymentGateway,
    loading: LoadingSendToPaymentGateway,
  } = usePaymentPlanAction(Action.SendToPaymentGateway, paymentPlan.id, () =>
    showMessage(t('Sending to Payment Gateway started')),
  );

  const shouldDisableExportXlsx =
    loadingExport ||
    !paymentPlan.can_export_xlsx ||
    paymentPlan.background_action_status ===
      PaymentPlanBackgroundActionStatus.XlsxExporting;

  const shouldDisableDownloadXlsx = !paymentPlan.can_download_xlsx;

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

  const handleExportAPI = async () => {
    try {
      await mutateExport({
        variables: {
          paymentPlanId: paymentPlan.id,
          fspXlsxTemplateId: selectedTemplate,
        },
      });
      showMessage(t('Exporting XLSX started'));
      handleClose();
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  const handleExport = async () => {
    try {
      await mutateExport({
        variables: {
          paymentPlanId: paymentPlan.id,
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
        {paymentPlan.can_create_follow_up && (
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
        {!paymentPlan.has_payment_list_export_file && (
          <Box m={2}>
            <LoadingButton
              loading={loadingExport}
              disabled={shouldDisableExportXlsx}
              color="primary"
              variant="contained"
              startIcon={<GetApp />}
              data-cy="button-export-xlsx"
              onClick={
                paymentPlan.fsp_communication_channel === 'API'
                  ? handleClickOpen
                  : handleExport
              }
            >
              {t('Export Xlsx')}
            </LoadingButton>
          </Box>
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
              onClick={handleExportAPI}
              data-cy="export-button"
              color="primary"
              disabled={!selectedTemplate}
            >
              {t('Export Xlsx')}
            </Button>
          </DialogActions>
        </Dialog>
        {paymentPlan.has_payment_list_export_file && (
          <>
            <Box m={2}>
              <Button
                color="primary"
                component="a"
                variant="contained"
                data-cy="button-download-xlsx"
                download
                href={`/api/download-payment-plan-payment-list/${paymentPlan.id}`}
                disabled={shouldDisableDownloadXlsx}
              >
                {t('Download XLSX')}
              </Button>
            </Box>
            {paymentPlan.can_send_xlsx_password && (
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
            )}
          </>
        )}

        {canSendToPaymentGateway && (
          <Box m={2}>
            <Button
              type="button"
              color="primary"
              variant="contained"
              onClick={() => sendToPaymentGateway()}
              data-cy="button-send-to-payment-gateway"
              disabled={LoadingSendToPaymentGateway}
            >
              {t('Send to FSP')}
            </Button>
          </Box>
        )}
      </>
    </Box>
  );
}
