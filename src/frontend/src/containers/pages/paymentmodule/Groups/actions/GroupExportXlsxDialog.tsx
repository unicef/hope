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
import { showApiErrorMessages } from '@utils/utils';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';

interface GroupExportXlsxDialogProps {
  groupId: string;
  /** When provided, sent as `exportTag` in the export request (batch re-export). */
  exportTag?: number;
  buttonLabel: string;
  dialogTitle: string;
  buttonVariant?: 'contained' | 'outlined';
  disabled?: boolean;
  /** Base suffix, e.g. `export-batch` → `button-export-batch`, `dialog-export-batch`. */
  dataCySuffix: string;
}

/**
 * Shared "export group delivery XLSX with optional FSP template" dialog used by
 * both the auth-code export on the group header and the batch re-export.
 */
export function GroupExportXlsxDialog({
  groupId,
  exportTag,
  buttonLabel,
  dialogTitle,
  buttonVariant = 'contained',
  disabled = false,
  dataCySuffix,
}: GroupExportXlsxDialogProps): ReactElement {
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
          id: groupId,
          requestBody: {
            ...(exportTag !== undefined ? { exportTag } : {}),
            fspXlsxTemplateId: selectedTemplate?.id ?? null,
          },
        },
      ),
    onSuccess: () => {
      showMessage(t('Export started'));
      queryClient.invalidateQueries({
        queryKey: ['paymentPlanGroup', businessArea, programId, groupId],
      });
      setOpen(false);
      setSelectedTemplate(null);
    },
    onError: (error) => {
      showApiErrorMessages(error, showMessage, t('Export failed'));
    },
  });

  const handleClose = (): void => {
    setOpen(false);
    setSelectedTemplate(null);
  };

  return (
    <>
      <Box m={2}>
        <LoadingButton
          loading={loadingExport}
          startIcon={<GetApp />}
          color="primary"
          variant={buttonVariant}
          onClick={() => setOpen(true)}
          disabled={disabled || loadingExport}
          data-cy={`button-${dataCySuffix}`}
        >
          {buttonLabel}
        </LoadingButton>
      </Box>
      <Dialog
        open={open}
        onClose={handleClose}
        scroll="paper"
        maxWidth="sm"
        fullWidth
      >
        <DialogTitleWrapper data-cy={`dialog-${dataCySuffix}`}>
          <DialogTitle>{dialogTitle}</DialogTitle>
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
            <Button onClick={handleClose}>{t('CANCEL')}</Button>
            <LoadingButton
              loading={loadingExport}
              color="primary"
              variant="contained"
              onClick={() => exportXlsx()}
              data-cy={`button-${dataCySuffix}-submit`}
            >
              {t('EXPORT')}
            </LoadingButton>
          </DialogActions>
        </DialogTitleWrapper>
      </Dialog>
    </>
  );
}
