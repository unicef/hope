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
import { PlanTypeEnum } from '@restgenerated/models/PlanTypeEnum';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import { showApiErrorMessages } from '@utils/utils';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { GroupExportPlanTypeOption, planTypeDisplayLabel } from '../utils';

interface GroupExportXlsxDialogProps {
  groupId: string;
  /** When provided, sent as `exportTag` in the export request (batch re-export). */
  exportTag?: number;
  /**
   * Exportable plan types to choose from; a select is shown when there is more than
   * one, a locked read-only field when there is exactly one. Omit (batch re-export)
   * to send no planType at all.
   */
  planTypeOptions?: GroupExportPlanTypeOption[];
  /**
   * Display-only plan type of the exported data when it is already fixed (batch
   * re-export: the batch's own type); shown as a locked field, never sent.
   */
  lockedPlanType?: PlanTypeEnum;
  /** Hide the FSP XLSX template picker (plain export resolves templates per plan). */
  showTemplateChoice?: boolean;
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
  planTypeOptions,
  lockedPlanType,
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
  const [selectedPlanType, setSelectedPlanType] =
    useState<GroupExportPlanTypeOption | null>(planTypeOptions?.[0] ?? null);
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
    enabled: open && showTemplateChoice && !!businessArea && !!programId,
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
            ...(selectedPlanType ? { planType: selectedPlanType.value } : {}),
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
    setSelectedPlanType(planTypeOptions?.[0] ?? null);
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
            {(lockedPlanType || planTypeOptions?.length === 1) && (
              <TextField
                label={t('Plan Type')}
                value={
                  lockedPlanType
                    ? planTypeDisplayLabel(lockedPlanType)
                    : (planTypeOptions?.[0]?.label ?? '')
                }
                size="small"
                fullWidth
                disabled
                data-cy={`locked-${dataCySuffix}-plan-type`}
                sx={{ mt: 1, mb: 2 }}
              />
            )}
            {!lockedPlanType && (planTypeOptions?.length ?? 0) > 1 && (
              <Autocomplete
                options={planTypeOptions ?? []}
                value={selectedPlanType}
                onChange={(_, value) => setSelectedPlanType(value)}
                getOptionLabel={(opt) => opt.label}
                isOptionEqualToValue={(a, b) => a.value === b.value}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label={t('Plan Type')}
                    size="small"
                    data-cy={`select-${dataCySuffix}-plan-type`}
                  />
                )}
                sx={{ mt: 1, mb: 2 }}
              />
            )}
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
              disabled={!!planTypeOptions?.length && !selectedPlanType}
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
