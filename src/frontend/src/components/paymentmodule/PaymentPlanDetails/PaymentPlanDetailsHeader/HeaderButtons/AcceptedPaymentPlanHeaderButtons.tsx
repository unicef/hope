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
import { BackgroundActionStatusEnum } from '@restgenerated/models/BackgroundActionStatusEnum';
import { PaymentPlanExportAuthCode } from '@restgenerated/models/PaymentPlanExportAuthCode';
import { SplitIntoPaymentLists } from '../SplitIntoPaymentLists';
import { ReactElement, useState } from 'react';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { showApiErrorMessages } from '@utils/utils';

export interface AcceptedPaymentPlanHeaderButtonsProps {
  canSendToPaymentGateway: boolean;
  canSplit: boolean;
  paymentPlan: PaymentPlanDetail;
  canClose: boolean;
}

export function AcceptedPaymentPlanHeaderButtons({
  canSendToPaymentGateway,
  canSplit,
  paymentPlan,
  canClose,
}: AcceptedPaymentPlanHeaderButtonsProps): ReactElement {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const { showMessage } = useSnackbar();
  const { businessArea, programId } = useBaseUrl();

  const { mutateAsync: closePaymentPlan, isPending: loadingClose } =
    useMutation({
      mutationFn: async () => {
        return RestService.restBusinessAreasProgramsPaymentPlansCloseRetrieve({
          businessAreaSlug: businessArea,
          programSlug: programId,
          id: paymentPlan.id,
        });
      },
      onSuccess: () => {
        showMessage(t('Payment plan closed successfully'));
      },
      onError: (error: any) => {
        showApiErrorMessages(error, showMessage);
      },
    });

  const { data, isLoading: loading } = useQuery({
    queryKey: ['fspXlsxTemplates', businessArea, programId],
    queryFn: async () => {
      return RestService.restBusinessAreasProgramsPaymentPlansFspXlsxTemplateListList(
        {
          businessAreaSlug: businessArea,
          programSlug: programId,
        },
      );
    },
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
      onError: (error: any) => {
        showApiErrorMessages(error, showMessage);
      },
    },
  );

  const { mutateAsync: mutateExport, isPending: loadingExport } = useMutation({
    mutationFn: async (variables: { fspXlsxTemplateId?: string }) => {
      const requestBody: PaymentPlanExportAuthCode = {
        fspXlsxTemplateId: variables.fspXlsxTemplateId || '',
      };
      return RestService.restBusinessAreasProgramsPaymentPlansGenerateXlsxWithAuthCodeCreate(
        {
          businessAreaSlug: businessArea,
          programSlug: programId,
          id: paymentPlan.id,
          requestBody,
        },
      );
    },
    onSuccess: () => {
      showMessage(t('Exporting XLSX started'));
    },
    onError: (error: any) => {
      showApiErrorMessages(error, showMessage);
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
    onError: (error: any) => {
      showApiErrorMessages(error, showMessage);
    },
  });

  const shouldDisableExportXlsx =
    loadingExport ||
    !paymentPlan.canExportXlsx ||
    paymentPlan.backgroundActionStatus ===
      BackgroundActionStatusEnum.XLSX_EXPORTING;

  const shouldDisableDownloadXlsx = !paymentPlan.canDownloadXlsx;

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
        fspXlsxTemplateId: selectedTemplate,
      });
      handleClose();
    } catch (e: any) {
      showApiErrorMessages(e, showMessage);
    }
  };

  const handleExport = async () => {
    try {
      await mutateExport({
        fspXlsxTemplateId: '',
      });
      handleClose();
    } catch (e: any) {
      showMessage(
        e?.body?.errors || e?.message || 'An error occurred while exporting',
      );
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
        {canClose && (
          <Box m={2}>
            <LoadingButton
              color="primary"
              variant="contained"
              data-cy="button-close"
              onClick={() => closePaymentPlan()}
              loading={loadingClose}
            >
              {t('Close')}
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
              {data?.results?.map((template) => (
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
