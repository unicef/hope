import { ContainerColumnWithBorder } from '@components/core/ContainerColumnWithBorder';
import { LoadingButton } from '@components/core/LoadingButton';
import { Title } from '@components/core/Title';
import {
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
import React, { useState } from 'react';
import {
  PaymentPlanDocument,
  PaymentPlanStatus,
  useAssignFundsCommitmentsPaymentPlanMutation,
} from '@generated/graphql';
import { LoadingButton } from '@components/core/LoadingButton';
import { useSnackbar } from '@hooks/useSnackBar';
import { usePermissions } from '@hooks/usePermissions';
import { hasPermissions, PERMISSIONS } from 'src/config/permissions';
import { Close } from '@mui/icons-material';
import { LabelizedField } from '@components/core/LabelizedField';
import { UniversalMoment } from '@components/core/UniversalMoment';

const EndInputAdornment = styled(InputAdornment)`
  margin-right: 10px;
`;

const XIcon = styled(Close)`
  color: #707070;
`;

interface FundsCommitmentSectionProps {
  paymentPlan: PaymentPlanDetail;
}

const FundsCommitmentSection: React.FC<FundsCommitmentSectionProps> = ({
  paymentPlan,
}) => {
  const initialFundsCommitment =
    paymentPlan?.fundsCommitments?.fundsCommitmentNumber || '';
  const initialFundsCommitmentItems =
    paymentPlan?.fundsCommitments?.fundsCommitmentItems?.map(
      (el) => el.recSerialNumber,
    ) || [];

  const [mutate, { loading: loadingAssign }] =
    useAssignFundsCommitmentsPaymentPlanMutation();

  const [selectedFundsCommitment, setSelectedFundsCommitment] =
    useState<string>(initialFundsCommitment);
  const [selectedItems, setSelectedItems] = useState<number[]>(
    initialFundsCommitmentItems,
  );

  const { showMessage } = useSnackbar();
  const permissions = usePermissions();

  const canAssignFunds = hasPermissions(
    PERMISSIONS.PM_ASSIGN_FUNDS_COMMITMENTS,
    permissions,
  );

  const handleFundsCommitmentChange = (event: SelectChangeEvent<string>) => {
    setSelectedFundsCommitment(event.target.value);
    setSelectedItems([]);
  };

  const availableFundsCommitments =
    paymentPlan?.availableFundsCommitments || [];
  const selectedCommitment = availableFundsCommitments.find(
    (commitment) =>
      commitment.fundsCommitmentNumber === String(selectedFundsCommitment),
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
      }
    }
  };

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
        {paymentPlan.status === PaymentPlanStatus.InReview ? (
          <>
            <Box mt={2}>
              <FormControl fullWidth size="small">
                <InputLabel>{t('Funds Commitment')}</InputLabel>
                <Select
                  size="small"
                  value={selectedFundsCommitment}
                  onChange={handleFundsCommitmentChange}
                  label={t('Funds Commitment')}
                >
                  <MenuItem value="">
                    <em>{t('None')}</em>
                  </MenuItem>
                  {availableFundsCommitments.map((commitment) => (
                    <MenuItem
                      key={commitment.fundsCommitmentNumber}
                      value={commitment.fundsCommitmentNumber}
                    >
                      {commitment.fundsCommitmentNumber}
                    </MenuItem>
                  ))}
                </Select>
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
                      !canAssignFunds || // Permission check
                      (selectedFundsCommitment && selectedItems.length === 0) || // Items required if commitment is filled
                      (!selectedFundsCommitment && selectedItems.length > 0) // Commitment required if items are filled
                    }
                  >
                    {t('Assign Funds Commitments')}
                  </LoadingButton>
                </span>
              </Tooltip>
            </Box>
          </>
        ) : (
          <>
            <Box mt={2}>
              {paymentPlan?.fundsCommitments?.fundsCommitmentItems?.map(
                (item, index) => (
                  <Box key={index} mb={4}>
                    <Typography variant="subtitle1" fontWeight="bold" mb={2}>
                      {t('Funds Commitment Item')} #{item.fundsCommitmentItem}
                    </Typography>
                    <Grid container spacing={3}>
                      <Grid size={3}>
                        <LabelizedField
                          label={t('Rec Serial Number')}
                          value={item.recSerialNumber}
                        />
                      </Grid>
                      <Grid size={3}>
                        <LabelizedField
                          label={t('Vendor ID')}
                          value={item.vendorId}
                        />
                      </Grid>
                      <Grid size={3}>
                        <LabelizedField
                          label={t('Business Area')}
                          value={item.businessArea}
                        />
                      </Grid>
                      <Grid size={3}>
                        <LabelizedField label={t('Posting Date')}>
                          <UniversalMoment>{item.postingDate}</UniversalMoment>
                        </LabelizedField>
                      </Grid>
                      <Grid size={3}>
                        <LabelizedField
                          label={t('Vision Approval')}
                          value={item.visionApproval}
                        />
                      </Grid>
                      <Grid size={3}>
                        <LabelizedField
                          label={t('Document Reference')}
                          value={item.documentReference}
                        />
                      </Grid>
                      <Grid size={3}>
                        <LabelizedField
                          label={t('FC Status')}
                          value={item.fcStatus}
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
                          label={t('Document Type')}
                          value={item.documentType}
                        />
                      </Grid>
                      <Grid size={3}>
                        <LabelizedField
                          label={t('Document Text')}
                          value={item.documentText}
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
                          label={t('GL Account')}
                          value={item.glAccount}
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
                          value={item.sponsor}
                        />
                      </Grid>
                      <Grid size={3}>
                        <LabelizedField
                          label={t('Sponsor Name')}
                          value={item.sponsorName}
                        />
                      </Grid>
                      <Grid size={3}>
                        <LabelizedField label={t('Fund')} value={item.fund} />
                      </Grid>
                      <Grid size={3}>
                        <LabelizedField
                          label={t('Funds Center')}
                          value={item.fundsCenter}
                        />
                      </Grid>
                      <Grid size={3}>
                        <LabelizedField
                          label={t('Percentage')}
                          value={item.percentage}
                        />
                      </Grid>
                      <Grid size={3}>
                        <LabelizedField label={t('Create Date')}>
                          <UniversalMoment>{item.createDate}</UniversalMoment>
                        </LabelizedField>
                      </Grid>
                      <Grid size={3}>
                        <LabelizedField
                          label={t('Created By')}
                          value={item.createdBy}
                        />
                      </Grid>
                      <Grid size={3}>
                        <LabelizedField label={t('Update Date')}>
                          <UniversalMoment>{item.updateDate}</UniversalMoment>
                        </LabelizedField>
                      </Grid>
                      <Grid size={3}>
                        <LabelizedField
                          label={t('Updated By')}
                          value={item.updatedBy}
                        />
                      </Grid>
                      <Grid size={3}>
                        <LabelizedField
                          label={t('Office ID')}
                          value={item.office?.id}
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
