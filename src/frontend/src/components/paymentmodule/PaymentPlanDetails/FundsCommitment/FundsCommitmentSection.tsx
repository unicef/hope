import React, { useMemo, useState } from 'react';
import {
  Autocomplete,
  TextField,
  Box,
  Typography,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Checkbox,
  ListItemText,
  SelectChangeEvent,
  IconButton,
  InputAdornment,
  Tooltip,
  styled,
  Grid2 as Grid,
} from '@mui/material';
import { ContainerColumnWithBorder } from '@components/core/ContainerColumnWithBorder';
import { Title } from '@components/core/Title';
import { t } from 'i18next';
import {
  FundsCommitmentNode,
  PaymentPlanDocument,
  PaymentPlanQuery,
  PaymentPlanStatus,
  useAssignFundsCommitmentsPaymentPlanMutation,
} from '@generated/graphql';
import { LoadingButton } from '@components/core/LoadingButton';
import { useSnackbar } from '@hooks/useSnackBar';
import { usePermissions } from '@hooks/usePermissions';
import { hasPermissions, PERMISSIONS } from 'src/config/permissions';
import { Close } from '@mui/icons-material';
import { LabelizedField } from '@components/core/LabelizedField';
import { WarningTooltip } from '@core/WarningTooltip';

const EndInputAdornment = styled(InputAdornment)`
  margin-right: 10px;
`;

const XIcon = styled(Close)`
  color: #707070;
`;

interface FundsCommitmentSectionProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
}

const FundsCommitmentSection: React.FC<FundsCommitmentSectionProps> = ({
  paymentPlan,
}) => {
  const initialFundsCommitment = paymentPlan?.fundsCommitments as FundsCommitmentNode | null;
  const initialFundsCommitmentItems =
    paymentPlan?.fundsCommitments?.fundsCommitmentItems?.map(
      (el) => el.recSerialNumber,
    ) || [];

  const [mutate, { loading: loadingAssign }] =
    useAssignFundsCommitmentsPaymentPlanMutation();

  const [selectedFundsCommitment, setSelectedFundsCommitment] =
    useState<FundsCommitmentNode | null>(initialFundsCommitment ?? null);
  const [selectedItems, setSelectedItems] = useState<number[]>(
    initialFundsCommitmentItems,
  );

  const { showMessage } = useSnackbar();
  const permissions = usePermissions();

  const canAssignFunds = hasPermissions(
    PERMISSIONS.PM_ASSIGN_FUNDS_COMMITMENTS,
    permissions,
  );

  const handleFundsCommitmentChange = (newValue: FundsCommitmentNode | null) => {
    setSelectedFundsCommitment(newValue);
    setSelectedItems([]);
  };

  const availableFundsCommitments =
    paymentPlan?.availableFundsCommitments || [];
  const selectedCommitment = availableFundsCommitments.find(
    (commitment) =>
      commitment.fundsCommitmentNumber === selectedFundsCommitment?.fundsCommitmentNumber,
  );

  const [isSubmittingFC, setIsSubmitting] = useState(false);

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
      setIsSubmitting(true);  // block button
      try {
        await mutate({
          variables: {
            paymentPlanId: paymentPlan.id,
            fundCommitmentItemsIds: selectedItems.map((number) =>
              number.toString(),
            ),
          },
          refetchQueries: () => [
            {
              query: PaymentPlanDocument,
              variables: { id: paymentPlan.id },
            },
          ],
        });
        showMessage(t('Funds commitment items assigned successfully'));
      } catch (error: any) {
        const errorMessages = error.graphQLErrors?.map(
          (x: any) => x.message,
        ) || [t('An error occurred while assigning funds commitments')];
        errorMessages.forEach((message) => showMessage(message));
      } finally {
    setIsSubmitting(false); // unblock button
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
        {paymentPlan.status === PaymentPlanStatus.InReview && (
          <>
            <Box mt={2}>
              <FormControl fullWidth size="small">
                <Autocomplete
                  value={selectedFundsCommitment}
                  onChange={(event, newValue) => handleFundsCommitmentChange(newValue as FundsCommitmentNode | null)}
                  options={availableFundsCommitments}
                  getOptionLabel={(option) => option.fundsCommitmentNumber || ''}
                  renderInput={(params) => (
                    <TextField {...params} label={t('Funds Commitment')} /> // The label is handled here
                  )}
                  renderOption={(props, option) => (
                    <MenuItem {...props} value={option.fundsCommitmentNumber}>
                      {option.fundsCommitmentNumber}
                    </MenuItem>
                  )}
                  isOptionEqualToValue={(option, value) => option.fundsCommitmentNumber === value?.fundsCommitmentNumber}
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
                      isSubmittingFC ||
                      !canAssignFunds || // Permission check
                      (selectedFundsCommitment && selectedItems.length === 0) || // Items required if commitment is filled
                      (!selectedFundsCommitment && selectedItems.length > 0) || // Commitment required if items are filled
                      isAlreadyAssigned  // don't allow assigning the same
                    }
                  >
                    {t('Assign Funds Commitments')}
                  </LoadingButton>
                </span>
              </Tooltip>
            </Box>
          </>
        )}
        {paymentPlan?.fundsCommitments?.fundsCommitmentItems?.length > 0 && (
          <>
            <Box mt={2}>
              {paymentPlan?.fundsCommitments?.fundsCommitmentNumber && (
                  <Typography variant="h6" fontWeight="bold" mb={2}>
                    {t('Funds Commitment Number')}: {selectedCommitment?.fundsCommitmentNumber} {paymentPlan.fundsCommitments.insufficientAmount && <WarningTooltip
                      message={t(
                        'Insufficient Commitment Amount',
                      )}
                    />}
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
          </>
        )}
      </ContainerColumnWithBorder>
    </Box>
  );
};

export default FundsCommitmentSection;
