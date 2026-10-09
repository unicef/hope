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
  Typography,
} from '@mui/material';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import { showApiErrorMessages } from '@utils/utils';
import type { ReactElement } from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';

interface GroupExportXlsxDialogProps {
  groupId: string;
  /** Hide the FSP XLSX template picker (plain export resolves templates per plan). */
  showTemplateChoice?: boolean;
  buttonLabel: string;
  dialogTitle: string;
  buttonVariant?: 'contained' | 'outlined';
  disabled?: boolean;
  /** Base suffix, e.g. `export-batch` → `button-export-batch`, `dialog-export-batch`. */
  dataCySuffix: string;
}

/** "Export group delivery XLSX with optional FSP template" dialog; exporting again replaces the group's file. */
export function GroupExportXlsxDialog({
  groupId,
  showTemplateChoice = true,
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
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsPaymentPlansFspXlsxTemplateListList,
      {
        businessAreaSlug: businessArea,
        programCode: programId,
        limit: 200,
      },
    ),
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlansFspXlsxTemplateListList({
        businessAreaSlug: businessArea,
        programCode: programId,
        limit: 200,
      }),
    enabled: open && showTemplateChoice && !!businessArea && !!programId,
  });
  const templateOptions = (templatesData?.results ?? []).map((tmpl) => ({
    id: tmpl.id,
    label: tmpl.name,
  }));

  const { mutate: exportXlsx, isPending: loadingExport } = useMutation({
    mutationFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlanGroupsDeliveryExportXlsxCreate(
        {
          businessAreaSlug: businessArea,
          programCode: programId,
          id: groupId,
          requestBody: {
            fspXlsxTemplateId: selectedTemplate?.id ?? null,
          },
        },
      ),
    onSuccess: () => {
      showMessage(t('Export started'));
      queryClient.invalidateQueries({
        queryKey: restQueryKey(
          RestService.restBusinessAreasProgramsPaymentPlanGroupsRetrieve,
        ),
      });
      setOpen(false);
      setSelectedTemplate(null);
    },
    onError: (error) => {
      showApiErrorMessages(error, showMessage, t('Export failed'));
    },
  });

  const handleOpen = (): void => {
    setOpen(true);
  };

  const handleClose = (): void => {
    setOpen(false);
    setSelectedTemplate(null);
  };

  return (
    <>
      <Box
        sx={{
          m: 2,
        }}
      >
        <LoadingButton
          loading={loadingExport}
          startIcon={<GetApp />}
          color="primary"
          variant={buttonVariant}
          onClick={handleOpen}
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
          {/* keep top padding despite MUI's `DialogTitle + DialogContent { padding-top: 0 }`,
              otherwise the first field's shrunk label is clipped */}
          <DialogContent sx={{ pt: '12px !important' }}>
            <Typography variant="body2" sx={{ mb: showTemplateChoice ? 2 : 0 }}>
              {t(
                'One payment list file is generated for every payment plan in this group. Exporting again replaces the current file.',
              )}
            </Typography>
            {showTemplateChoice && (
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
            )}
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
