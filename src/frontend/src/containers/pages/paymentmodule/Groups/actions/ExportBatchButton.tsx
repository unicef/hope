import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { LoadingButton } from '@core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import { GetApp } from '@mui/icons-material';
import { showApiErrorMessages } from '@utils/utils';
import {
  Autocomplete,
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogTitle,
  TextField,
} from '@mui/material';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';

interface ExportBatchButtonProps {
  groupId: string;
  tag: string;
  isBusy?: boolean;
}

export function ExportBatchButton({
  groupId,
  tag,
  isBusy = false,
}: ExportBatchButtonProps): ReactElement {
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

  const { mutateAsync: exportBatch, isPending: loadingExport } = useMutation({
    mutationFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlanGroupsDeliveryExportXlsxCreate(
        {
          businessAreaSlug: businessArea,
          programCode: programId,
          id: groupId,
          requestBody: {
            exportTag: parseInt(tag, 10),
            fspXlsxTemplateId: selectedTemplate?.id ?? null,
          },
        },
      ),
    onSuccess: () => {
      showMessage(t('Export started'));
      queryClient.invalidateQueries({
        queryKey: ['paymentPlanGroup', businessArea, programId, groupId],
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

  const isDisabled = !groupId || !tag || loadingExport || isBusy;

  return (
    <>
      <Box m={2}>
        <LoadingButton
          loading={loadingExport}
          startIcon={<GetApp />}
          color="primary"
          variant="contained"
          onClick={() => setOpen(true)}
          disabled={isDisabled}
          data-cy="button-export-batch"
        >
          {t('Re-export Batch')}
        </LoadingButton>
      </Box>
      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        scroll="paper"
        maxWidth="sm"
        fullWidth
      >
        <DialogTitleWrapper data-cy="dialog-export-batch">
          <DialogTitle>{t('Re-export Batch #{{tag}}', { tag })}</DialogTitle>
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
              onClick={() => exportBatch()}
              data-cy="button-export-batch-submit"
            >
              {t('EXPORT')}
            </LoadingButton>
          </DialogActions>
        </DialogTitleWrapper>
      </Dialog>
    </>
  );
}
