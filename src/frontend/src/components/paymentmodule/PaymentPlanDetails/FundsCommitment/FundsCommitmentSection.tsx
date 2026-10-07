import { LabelizedField } from '@components/core/LabelizedField';
import { hasPermissions, PERMISSIONS } from 'src/config/permissions';
import { ContainerColumnWithBorder } from '@components/core/ContainerColumnWithBorder';
import { LoadingButton } from '@components/core/LoadingButton';
import { Title } from '@components/core/Title';
import React, { useMemo, useState } from 'react';
import {
  Autocomplete,
  TextField,
  Box,
  FormControl,
  Tooltip,
  Typography,
  Grid,
} from '@mui/material';
import type { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { t } from 'i18next';
import { PaymentPlanStatusEnum } from '@restgenerated/models/PaymentPlanStatusEnum';
import { useSnackbar } from '@hooks/useSnackBar';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { formatFigure, showApiErrorMessages } from '@utils/utils';

interface FundsCommitmentSectionProps {
  paymentPlan: PaymentPlanDetail;
}

const FundsCommitmentSection: React.FC<FundsCommitmentSectionProps> = ({
  paymentPlan,
}) => {
  const visionManaged = paymentPlan.visionManaged;
  const initialFundsCommitments = useMemo(
    () => paymentPlan.fundsCommitments || [],
    [paymentPlan.fundsCommitments],
  );

  const queryClient = useQueryClient();
  const { showMessage } = useSnackbar();
  const permissions = usePermissions();
  const { businessArea } = useBaseUrl();
  const { mutateAsync: assignFundsCommitment, isPending: loadingAssign } =
    useMutation({
      mutationFn: async ({
        fundsCommitmentNumbers,
      }: {
        fundsCommitmentNumbers: string[];
      }) => {
        return RestService.restBusinessAreasProgramsPaymentPlansAssignFundsCommitmentsCreate(
          {
            businessAreaSlug: businessArea,
            programCode: paymentPlan.program.code,
            id: paymentPlan.id,
            requestBody: { fundsCommitmentNumbers },
          },
        );
      },
      onSuccess: () => {
        queryClient.invalidateQueries({
          queryKey: restQueryKey(
            RestService.restBusinessAreasProgramsPaymentPlansRetrieve,
          ),
        });
      },
    });

  const [selectedFundsCommitments, setSelectedFundsCommitments] = useState(
    initialFundsCommitments,
  );

  const canAssignFunds = hasPermissions(
    PERMISSIONS.PM_ASSIGN_FUNDS_COMMITMENTS,
    permissions,
  );

  const availableFundsCommitments = useMemo(
    () => paymentPlan?.availableFundsCommitments || [],
    [paymentPlan],
  );
  const handleSubmit = async () => {
    if (selectedFundsCommitments.length > 0) {
      try {
        await assignFundsCommitment({
          fundsCommitmentNumbers: selectedFundsCommitments.map(
            (header) => header.fundsCommitmentNumber,
          ),
        });
        showMessage(t('Funds commitment headers assigned successfully'));
        await queryClient.invalidateQueries({
          queryKey: restQueryKey(
            RestService.restBusinessAreasProgramsPaymentPlansRetrieve,
          ),
        });
      } catch (e) {
        showApiErrorMessages(e, showMessage);
      }
    }
  };

  const isAlreadyAssigned = useMemo(() => {
    if (selectedFundsCommitments.length !== initialFundsCommitments.length) {
      return false;
    }
    const assignedNumbers = new Set(
      initialFundsCommitments.map((header) => header.fundsCommitmentNumber),
    );
    return selectedFundsCommitments.every((header) =>
      assignedNumbers.has(header.fundsCommitmentNumber),
    );
  }, [initialFundsCommitments, selectedFundsCommitments]);

  return (
    <Box
      sx={{
        m: 5,
      }}
    >
      <ContainerColumnWithBorder>
        <Box
          sx={{
            mt: 4,
          }}
        >
          <Title>
            <Typography variant="h6">{t('Funds Commitment')}</Typography>
          </Title>
        </Box>
        {paymentPlan.status === PaymentPlanStatusEnum.IN_REVIEW &&
          !visionManaged && (
            <React.Fragment>
              <Box
                sx={{
                  mt: 2,
                }}
              >
                <FormControl fullWidth size="small">
                  <Autocomplete
                    multiple
                    value={selectedFundsCommitments}
                    onChange={(_event, newValue) =>
                      setSelectedFundsCommitments(newValue)
                    }
                    options={availableFundsCommitments}
                    getOptionLabel={(option) =>
                      option?.fundsCommitmentNumber || ''
                    }
                    renderInput={(params) => (
                      <TextField
                        {...params}
                        label={t('Funds Commitment Headers')}
                      />
                    )}
                    renderOption={(props, option) => {
                      const { key, ...optionProps } = props;
                      return (
                        <li key={key} {...optionProps}>
                          {option.fundsCommitmentNumber}
                        </li>
                      );
                    }}
                    isOptionEqualToValue={(option, value) =>
                      option.fundsCommitmentNumber ===
                      value?.fundsCommitmentNumber
                    }
                    noOptionsText={t('No options')}
                    clearOnEscape
                  />
                </FormControl>
              </Box>
              <Box
                sx={{
                  mt: 3,
                }}
              >
                <Tooltip
                  title={!canAssignFunds ? t('Permission Denied') : ''}
                  arrow
                >
                  <span>
                    <LoadingButton
                      variant="contained"
                      loading={loadingAssign}
                      color="primary"
                      onClick={handleSubmit}
                      disabled={
                        loadingAssign ||
                        !canAssignFunds ||
                        selectedFundsCommitments.length === 0 ||
                        isAlreadyAssigned
                      }
                    >
                      {t('Assign Funds Commitments')}
                    </LoadingButton>
                  </span>
                </Tooltip>
              </Box>
            </React.Fragment>
          )}
        {initialFundsCommitments.length > 0 ? (
          initialFundsCommitments.map((header, headerIndex) => (
            <Box
              key={header.id}
              sx={{
                mt: 2,
                borderBottom:
                  headerIndex < initialFundsCommitments.length - 1
                    ? '1px solid #e0e0e0'
                    : undefined,
              }}
            >
              <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 2 }}>
                {t('Funds Commitment Number')}: {header.fundsCommitmentNumber}
              </Typography>
              <Grid container spacing={3} sx={{ mb: 3 }}>
                <Grid size={3}>
                  <LabelizedField label={t('Vendor')} value={header.vendorId} />
                </Grid>
                <Grid size={3}>
                  <LabelizedField
                    label={t('Posting Date')}
                    value={header.postingDate}
                  />
                </Grid>
                <Grid size={3}>
                  <LabelizedField
                    label={t('Document Reference')}
                    value={header.documentReference}
                  />
                </Grid>
                <Grid size={3}>
                  <LabelizedField label={t('Status')} value={header.fcStatus} />
                </Grid>
                <Grid size={3}>
                  <LabelizedField
                    label={t('Total Amount USD')}
                    value={formatFigure(header.totalAmountUsd)}
                  />
                </Grid>
                <Grid size={3}>
                  <LabelizedField
                    label={t('Total Amount Local')}
                    value={formatFigure(header.totalAmountLocal)}
                  />
                </Grid>
                <Grid size={3}>
                  <LabelizedField label={t('Currency')} value={header.currency} />
                </Grid>
              </Grid>
              {header.fundsCommitmentItems.map((item, itemIndex) => (
                <Box key={item.recSerialNumber} sx={{ mb: 4 }}>
                  <Typography
                    variant="subtitle1"
                    sx={{ fontWeight: 'bold', mb: 2 }}
                  >
                    {t('Item')} #{item.fundsCommitmentItem}
                  </Typography>
                  <Grid container spacing={3}>
                    <Grid size={3}>
                      <LabelizedField
                        label={t('Business Area')}
                        value={item.businessArea}
                      />
                    </Grid>
                    <Grid size={3}>
                      <LabelizedField
                        label={t('WBS Element')}
                        value={item.wbsElement}
                      />
                    </Grid>
                    <Grid size={3}>
                      <LabelizedField
                        label={t('Grant Number')}
                        value={item.grantNumber}
                      />
                    </Grid>
                    <Grid size={3}>
                      <LabelizedField
                        label={t('Currency Code')}
                        value={item.currencyCode}
                      />
                    </Grid>
                    <Grid size={3}>
                      <LabelizedField
                        label={t('Commitment Amount Local')}
                        value={formatFigure(item.commitmentAmountLocal)}
                      />
                    </Grid>
                    <Grid size={3}>
                      <LabelizedField
                        label={t('Commitment Amount USD')}
                        value={formatFigure(item.commitmentAmountUsd)}
                      />
                    </Grid>
                    <Grid size={3}>
                      <LabelizedField
                        label={t('Total Open Amount Local')}
                        value={formatFigure(item.totalOpenAmountLocal)}
                      />
                    </Grid>
                    <Grid size={3}>
                      <LabelizedField
                        label={t('Total Open Amount USD')}
                        value={formatFigure(item.totalOpenAmountUsd)}
                      />
                    </Grid>
                    <Grid size={3}>
                      <LabelizedField
                        label={t('Sponsor')}
                        value={`${item.sponsor ?? '-'} ${item.sponsorName ?? '-'}`}
                      />
                    </Grid>
                  </Grid>
                  {itemIndex < header.fundsCommitmentItems.length - 1 && (
                    <Box
                      sx={{
                        borderBottom: '1px solid #e0e0e0',
                        my: 3,
                        width: '100%',
                      }}
                    />
                  )}
                </Box>
              ))}
            </Box>
          ))
        ) : (
          <Typography variant="body1" sx={{ mt: 2 }}>
            {t('No funds commitment headers assigned')}
          </Typography>
        )}
      </ContainerColumnWithBorder>
    </Box>
  );
};

export default FundsCommitmentSection;
