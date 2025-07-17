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
  Checkbox,
  FormControl,
  IconButton,
  InputAdornment,
  InputLabel,
  ListItemText,
  MenuItem,
  Select,
  SelectChangeEvent,
  styled,
  Tooltip,
  Typography,
  Grid2 as Grid,
} from '@mui/material';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { t } from 'i18next';
import { PaymentPlanStatusEnum } from '@restgenerated/models/PaymentPlanStatusEnum';
import { useSnackbar } from '@hooks/useSnackBar';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { WarningTooltip } from '@core/WarningTooltip';

const EndInputAdornment = styled(InputAdornment)`
  margin-right: 10px;
`;

import { Close } from '@mui/icons-material';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
const XIcon = styled(Close)`
  color: #707070;
`;

interface FundsCommitmentSectionProps {
  paymentPlan: PaymentPlanDetail;
}

const FundsCommitmentSection: React.FC<FundsCommitmentSectionProps> = ({
  paymentPlan,
}) => {
  const initialFundsCommitment = paymentPlan?.fundsCommitments || null;
  const initialFundsCommitmentItems =
    paymentPlan?.fundsCommitments?.fundsCommitmentItems?.map(
      (el) => el.recSerialNumber,
    ) || [];

  const queryClient = useQueryClient();
  const { showMessage } = useSnackbar();
  const permissions = usePermissions();
  const { businessArea } = useBaseUrl();
  const { mutateAsync: assignFundsCommitment, isPending: loadingAssign } =
    useMutation({
      mutationFn: async ({
        fundCommitmentItemsIds,
      }: {
        fundCommitmentItemsIds: string[];
      }) => {
        return RestService.restBusinessAreasProgramsPaymentPlansAssignFundsCommitmentsCreate(
          {
            businessAreaSlug: businessArea,
            programSlug: paymentPlan.program.slug,
            id: paymentPlan.id,
            requestBody: { fundCommitmentItemsIds },
          },
        );
      },
      onSuccess: () => {
        queryClient.invalidateQueries({
          queryKey: ['paymentPlan', paymentPlan.id],
        });
      },
    });

  const [selectedFundsCommitment, setSelectedFundsCommitment] = useState(
    initialFundsCommitment,
  );
  const [selectedItems, setSelectedItems] = useState<number[]>(
    initialFundsCommitmentItems,
  );

  const canAssignFunds = hasPermissions(
    PERMISSIONS.PM_ASSIGN_FUNDS_COMMITMENTS,
    permissions,
  );

  const handleFundsCommitmentChange = (newValue: any) => {
    setSelectedFundsCommitment(newValue);
    setSelectedItems([]);
  };

  const availableFundsCommitments =
    paymentPlan?.availableFundsCommitments || [];
  const selectedCommitment = availableFundsCommitments.find(
    (commitment) =>
      commitment.fundsCommitmentNumber ===
      selectedFundsCommitment?.fundsCommitmentNumber,
  );

  const handleItemsChange = (event: SelectChangeEvent<string[]>) => {
    const value = event.target.value as string[];

    if (value.includes('select-all')) {
      const allItems =
        selectedCommitment?.fundsCommitmentItems.map(
          (item) => item.recSerialNumber,
        ) || [];
      if (selectedItems.length === allItems.length) {
        setSelectedItems([]); // Deselect all
      } else {
        setSelectedItems(allItems); // Select all
      }
    } else {
      const clickedItem = Number(value[value.length - 1]); // Get the last clicked item
      if (selectedItems.includes(clickedItem)) {
        // If the item is already selected, remove it
        setSelectedItems(selectedItems.filter((item) => item !== clickedItem));
      } else {
        // If the item is not selected, add it
        setSelectedItems([...selectedItems, clickedItem]);
      }
    }
  };

  const handleSubmit = async () => {
    if (paymentPlan) {
      try {
        await assignFundsCommitment({
          fundCommitmentItemsIds: selectedItems.map((number) =>
            number.toString(),
          ),
        });
        showMessage(t('Funds commitment items assigned successfully'));
      } catch (error: any) {
        const errorMessages = error?.graphQLErrors?.map(
          (x: any) => x.message,
        ) || [t('An error occurred while assigning funds commitments')];
        errorMessages.forEach((message) => showMessage(message));
      }
    }
  };

  const isSameSelection = (a_set: number[], b_set: number[]) => {
    if (a_set.length !== b_set.length) return false;
    const setA = new Set(a_set);
    return b_set.every((item) => setA.has(item));
  };

  const assignedFundsCommitmentItems = useMemo(
    () =>
      paymentPlan?.fundsCommitments?.fundsCommitmentItems?.map(
        (item) => item.recSerialNumber,
      ) || [],
    [paymentPlan],
  );

  const isAlreadyAssigned = useMemo(() => {
    return isSameSelection(selectedItems, assignedFundsCommitmentItems);
  }, [selectedItems, assignedFundsCommitmentItems]);

  const clearItems = () => {
    setSelectedItems([]);
  };

  return (
    <Box m={5}>
      <ContainerColumnWithBorder>
        <Box mt={4}>
          <Title>
            <Typography variant="h6">{t('Funds Commitment')}</Typography>
          </Title>
        </Box>
        {paymentPlan.status === PaymentPlanStatusEnum.IN_REVIEW && (
          <React.Fragment>
            <Box mt={2}>
              <FormControl fullWidth size="small">
                <Autocomplete
                  value={selectedFundsCommitment}
                  onChange={(_event, newValue) =>
                    handleFundsCommitmentChange(newValue)
                  }
                  options={availableFundsCommitments}
                  getOptionLabel={(option) =>
                    option.fundsCommitmentNumber || ''
                  }
                  renderInput={(params) => (
                    <TextField {...params} label={t('Funds Commitment')} />
                  )}
                  renderOption={(props, option) => (
                    <MenuItem {...props} value={option.fundsCommitmentNumber}>
                      {option.fundsCommitmentNumber}
                    </MenuItem>
                  )}
                  isOptionEqualToValue={(option, value) =>
                    option.fundsCommitmentNumber ===
                    value?.fundsCommitmentNumber
                  }
                  noOptionsText={t('No options')}
                  clearOnEscape
                />
              </FormControl>
            </Box>
            {selectedCommitment && (
              <Box mt={2}>
                <FormControl fullWidth size="small">
                  <InputLabel>{t('Funds Commitment Items')}</InputLabel>
                  <Select
                    multiple
                    label={t('Funds Commitment Items')}
                    value={selectedItems.map(String)}
                    onChange={handleItemsChange}
                    renderValue={(selected) => selected.join(', ')}
                    endAdornment={
                      <EndInputAdornment position="end">
                        <IconButton
                          size="medium"
                          onMouseDown={(event) => {
                            event.preventDefault();
                            clearItems();
                          }}
                        >
                          <XIcon fontSize="small" />
                        </IconButton>
                      </EndInputAdornment>
                    }
                  >
                    <MenuItem value="select-all">
                      <Checkbox
                        checked={
                          selectedCommitment?.fundsCommitmentItems.length > 0 &&
                          selectedCommitment.fundsCommitmentItems.every(
                            (item) =>
                              selectedItems.includes(item.recSerialNumber),
                          )
                        }
                        indeterminate={
                          selectedCommitment?.fundsCommitmentItems.some(
                            (item) =>
                              selectedItems.includes(item.recSerialNumber),
                          ) &&
                          !selectedCommitment.fundsCommitmentItems.every(
                            (item) =>
                              selectedItems.includes(item.recSerialNumber),
                          )
                        }
                      />
                      <ListItemText primary={t('Select All')} />
                    </MenuItem>
                    {selectedCommitment.fundsCommitmentItems.map((item) => (
                      <MenuItem
                        key={item.recSerialNumber}
                        value={item.recSerialNumber}
                      >
                        <Checkbox
                          checked={selectedItems.includes(item.recSerialNumber)}
                        />
                        <ListItemText
                          primary={`${item.fundsCommitmentItem} - ${item.recSerialNumber}`}
                        />
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Box>
            )}
            <Box mt={3}>
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
                      (selectedFundsCommitment && selectedItems.length === 0) ||
                      (!selectedFundsCommitment && selectedItems.length > 0) ||
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
        {paymentPlan?.fundsCommitments?.fundsCommitmentItems?.length > 0 && (
          <React.Fragment>
            <Box mt={2}>
              {paymentPlan?.fundsCommitments?.fundsCommitmentNumber && (
                <Typography variant="h6" fontWeight="bold" mb={2}>
                  {t('Funds Commitment Number')}:{' '}
                  {selectedCommitment.fundsCommitmentNumber}{' '}
                  {paymentPlan.fundsCommitments.insufficientAmount && (
                    <WarningTooltip
                      message={t('Insufficient Commitment Amount')}
                    />
                  )}
                </Typography>
              )}
              {paymentPlan?.fundsCommitments?.fundsCommitmentItems?.map(
                (item, index) => (
                  <Box key={index} mb={4}>
                    <Typography variant="subtitle1" fontWeight="bold" mb={2}>
                      {t('Item')} #{item.fundsCommitmentItem}
                    </Typography>
                    <Grid container spacing={3}>
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
                          value={item.commitmentAmountLocal}
                        />
                      </Grid>
                      <Grid size={3}>
                        <LabelizedField
                          label={t('Commitment Amount USD')}
                          value={item.commitmentAmountUsd}
                        />
                      </Grid>
                      <Grid size={3}>
                        <LabelizedField
                          label={t('Total Open Amount Local')}
                          value={item.totalOpenAmountLocal}
                        />
                      </Grid>
                      <Grid size={3}>
                        <LabelizedField
                          label={t('Total Open Amount USD')}
                          value={item.totalOpenAmountUsd}
                        />
                      </Grid>
                      <Grid size={3}>
                        <LabelizedField
                          label={t('Sponsor')}
                          value={`${item.sponsor ?? '-'} ${item.sponsorName ?? '-'}`}
                        />
                      </Grid>
                    </Grid>
                    {index <
                      paymentPlan?.fundsCommitments?.fundsCommitmentItems
                        ?.length -
                        1 && (
                      <Box
                        sx={{
                          borderBottom: '1px solid #e0e0e0',
                          my: 3,
                          width: '100%',
                        }}
                      />
                    )}
                  </Box>
                ),
              )}
              {(!paymentPlan?.fundsCommitments ||
                !paymentPlan?.fundsCommitments?.fundsCommitmentItems
                  ?.length) && (
                <Typography variant="body1">
                  {t('No funds commitment items assigned')}
                </Typography>
              )}
            </Box>
          </React.Fragment>
        )}
      </ContainerColumnWithBorder>
    </Box>
  );
};

export default FundsCommitmentSection;
