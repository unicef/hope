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
import { useBaseUrl } from '@hooks/useBaseUrl';
import { LoadingButton } from '../../../../core/LoadingButton';
import { CreateFollowUpPaymentPlan } from '../../../CreateFollowUpPaymentPlan';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQuery } from '@tanstack/react-query';
import { PaymentPlanBackgroundActionStatusEnum } from '@restgenerated/models/PaymentPlanBackgroundActionStatusEnum';
import { SplitIntoPaymentLists } from '../SplitIntoPaymentLists';
import { ReactElement, useState } from 'react';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { PaginatedFSPXlsxTemplateList } from '@restgenerated/models/PaginatedFSPXlsxTemplateList';

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
  const { businessArea, programId } = useBaseUrl();

  const {
    data: templateData,
    isLoading: loadingTemplates,
    error: errorTemplates,
  } = useQuery<PaginatedFSPXlsxTemplateList>({
    queryKey: ['fsp-xlsx-templates', businessArea, programId],
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlansFspXlsxTemplateListList({
        businessAreaSlug: businessArea,
        programSlug: programId,
      }),
    enabled: !!businessArea && !!programId,
  });

  const { mutateAsync: sendXlsxPassword, isPending: loadingSend } = useMutation(
    {
      mutationFn: () =>
        RestService.restBusinessAreasProgramsPaymentPlansSendXlsxPasswordRetrieve(
          {
            businessAreaSlug: businessArea,
            programSlug: programId,
            id: paymentPlan.id,
          },
        ),
      onSuccess: () => {
        showMessage(t('Password has been sent.'));
      },
      onError: (error) => {
        showMessage(
          error.message || t('An error occurred while sending the password'),
        );
      },
    },
  );

  const { mutateAsync: exportReconciliationXlsx, isPending: loadingExport } =
    useMutation({
      mutationFn: () =>
        RestService.restBusinessAreasProgramsPaymentPlansReconciliationExportXlsxRetrieve(
          {
            businessAreaSlug: businessArea,
            programSlug: programId,
            id: paymentPlan.id,
          },
        ),
      onSuccess: () => {
        showMessage(t('Exporting XLSX started'));
      },
      onError: (error) => {
        showMessage(
          error.message || t('An error occurred while exporting XLSX'),
        );
      },
    });

  const {
    mutateAsync: sendToPaymentGateway,
    isPending: LoadingSendToPaymentGateway,
  } = useMutation({
    mutationFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlansSendToPaymentGatewayRetrieve(
        {
          businessAreaSlug: businessArea,
          programSlug: programId,
          id: paymentPlan.id,
        },
      ),
    onSuccess: () => {
      showMessage(t('Sending to Payment Gateway started'));
    },
    onError: (error) => {
      showMessage(
        error.message ||
          t('An error occurred while sending to payment gateway'),
      );
    },
  });

  const shouldDisableExportXlsx =
    loadingExport ||
    !paymentPlan.canExportXlsx ||
    paymentPlan.backgroundActionStatus ===
      PaymentPlanBackgroundActionStatusEnum.XLSX_EXPORTING;

  const shouldDisableDownloadXlsx = !paymentPlan.canDownloadXlsx;

  if (loadingTemplates) return <LoadingComponent />;
  if (errorTemplates) return null;
  if (!templateData) return null;

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
      await exportReconciliationXlsx();
      handleClose();
    } catch (e) {
      // Error handling is managed by the mutation's onError callback
    }
  };

  const handleExport = async () => {
    try {
      await exportReconciliationXlsx();
      handleClose();
    } catch (e) {
      // Error handling is managed by the mutation's onError callback
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
        {!paymentPlan.hasPaymentListExportFile && (
          <Box m={2}>
            <LoadingButton
              loading={loadingExport}
              disabled={shouldDisableExportXlsx}
              color="primary"
              variant="contained"
              startIcon={<GetApp />}
              data-cy="button-export-xlsx"
              onClick={
                paymentPlan.fspCommunicationChannel === 'API'
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
              {templateData?.results?.map((template) => (
                <MenuItem key={template.id} value={template.id}>
                  {template.name}
                </MenuItem>
              ))}
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
        {paymentPlan.hasPaymentListExportFile && (
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
            {paymentPlan.canSendXlsxPassword && (
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
