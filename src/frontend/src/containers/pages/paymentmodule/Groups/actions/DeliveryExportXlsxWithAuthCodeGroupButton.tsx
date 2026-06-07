import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { LoadingButton } from '@core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { GetApp } from '@mui/icons-material';
import {
  Autocomplete,
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  TextField,
} from '@mui/material';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { showApiErrorMessages } from '@utils/utils';
import { PaymentPlanGroupDetail } from '../types';
import { isGroupBackgroundActionBusy } from '../utils';

interface DeliveryExportXlsxWithAuthCodeGroupButtonProps {
  group: PaymentPlanGroupDetail | null;
}

export function DeliveryExportXlsxWithAuthCodeGroupButton({
  group,
}: DeliveryExportXlsxWithAuthCodeGroupButtonProps): ReactElement {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<{
    id: string;
    label: string;
  } | null>(null);
  const { businessArea, programId } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const queryClient = useQueryClient();

  const { data: templatesData } = useQuery({
    queryKey: ['fspXlsxTemplates', businessArea, programId],
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlansFspXlsxTemplateListList({
        businessAreaSlug: businessArea,
        programCode: programId,
        limit: 200,
      }),
    enabled: open && !!businessArea && !!programId,
  });
  const templateOptions = (templatesData?.results ?? []).map((tmpl) => ({
    id: tmpl.id,
    label: tmpl.name,
  }));

  const { mutateAsync: exportXlsx, isPending: loadingExport } = useMutation({
    mutationFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlanGroupsDeliveryExportXlsxCreate(
        {
          businessAreaSlug: businessArea,
          programCode: programId,
          id: group?.id,
          requestBody: {
            fspXlsxTemplateId: selectedTemplate?.id ?? null,
          },
        },
      ),
    onSuccess: () => {
      showMessage(t('Export started'));
      queryClient.invalidateQueries({
        queryKey: ['paymentPlanGroup', businessArea, programId, group?.id],
      });
      queryClient.invalidateQueries({ queryKey: ['businessAreasPaymentPlans'] });
      queryClient.invalidateQueries({ queryKey: ['businessAreasProgramsPaymentPlansList'] });
      setOpen(false);
      setSelectedTemplate(null);
    },
    onError: (error: any) => {
      showApiErrorMessages(error, showMessage, t('Export failed'));
    },
  });

  const isDisabled = !group || loadingExport || isGroupBackgroundActionBusy(group);

  return (
    <>
      <Box m={2}>
        <Button
          startIcon={<GetApp />}
          color="primary"
          variant="outlined"
          onClick={() => setOpen(true)}
          disabled={isDisabled}
          data-cy="button-delivery-export-xlsx-with-auth-code-group"
        >
          {t('Export with Auth Code')}
        </Button>
      </Box>
      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        scroll="paper"
        maxWidth="sm"
        fullWidth
      >
        <DialogTitleWrapper data-cy="dialog-delivery-export-xlsx-with-auth-code-group">
          <DialogTitle>{t('Export with Auth Code')}</DialogTitle>
          <DialogContent>
            <Autocomplete
              options={templateOptions}
              value={selectedTemplate}
              onChange={(_, value) => setSelectedTemplate(value)}
              getOptionLabel={(opt) => opt.label}
              isOptionEqualToValue={(a, b) => a.id === b.id}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label={t('FSP XLSX Template (optional)')}
                  size="small"
                />
              )}
              sx={{ mt: 1 }}
            />
          </DialogContent>
          <DialogActions>
            <Button
              onClick={() => {
                setOpen(false);
                setSelectedTemplate(null);
              }}
            >
              {t('CANCEL')}
            </Button>
            <LoadingButton
              loading={loadingExport}
              color="primary"
              variant="contained"
              onClick={() => exportXlsx()}
              data-cy="button-delivery-export-xlsx-with-auth-code-group-submit"
            >
              {t('EXPORT')}
            </LoadingButton>
          </DialogActions>
        </DialogTitleWrapper>
      </Dialog>
    </>
  );
}
