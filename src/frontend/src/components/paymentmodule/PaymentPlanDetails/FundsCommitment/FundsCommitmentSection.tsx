import React, { useState } from 'react';
import {
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
} from '@mui/material';
import { ContainerColumnWithBorder } from '@components/core/ContainerColumnWithBorder';
import { Title } from '@components/core/Title';
import { t } from 'i18next';
import {
  PaymentPlanQuery,
  useAssignFundsCommitmentsPaymentPlanMutation,
} from '@generated/graphql';
import { LoadingButton } from '@components/core/LoadingButton';
import { useSnackbar } from '@hooks/useSnackBar';
import { usePermissions } from '@hooks/usePermissions';
import { hasPermissions, PERMISSIONS } from 'src/config/permissions';
import { Close } from '@mui/icons-material';

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
  const initialFundsCommitment =
    paymentPlan?.fundsCommitments?.fundsCommitmentNumber || '';
  const initialFundsCommitmentItems =
    paymentPlan?.fundsCommitments?.fundsCommitmentItems?.map(
      (el) => el.recSerialNumber,
    );

  const [mutate, { loading: loadingAssign }] =
    useAssignFundsCommitmentsPaymentPlanMutation();

  const [selectedFundsCommitment, setSelectedFundsCommitment] =
    useState<string>(initialFundsCommitment || '');
  const [selectedItems, setSelectedItems] = useState<string[]>(
    initialFundsCommitmentItems || [],
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

  const availableFundsCommitments = paymentPlan.availableFundsCommitments || [];
  const selectedCommitment = availableFundsCommitments.find(
    (commitment) =>
      commitment.fundsCommitmentNumber === String(selectedFundsCommitment),
  );

  const handleItemsChange = (event: SelectChangeEvent<string[]>) => {
    const value = event.target.value as string[];
    if (value.includes('select-all')) {
      const allItems =
        selectedCommitment?.fundsCommitmentItems.map((item) =>
          item.recSerialNumber.toString(),
        ) || [];
      if (selectedItems.length === allItems.length) {
        setSelectedItems([]);
      } else {
        setSelectedItems(allItems);
      }
    } else {
      setSelectedItems(value);
    }
  };

  const handleSubmit = async () => {
    if (paymentPlan && selectedItems.length > 0) {
      try {
        await mutate({
          variables: {
            paymentPlanId: paymentPlan?.id,
            fundCommitmentItemsIds: selectedItems,
          },
        });
        showMessage('Funds commitment items assigned successfully');
      } catch (e) {
        e.graphQLErrors.map((x) => showMessage(x.message));
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
        <Box mt={2}>
          <FormControl fullWidth size="small">
            <InputLabel>{t('Select Funds Commitment')}</InputLabel>
            <Select
              size="small"
              value={selectedFundsCommitment}
              onChange={handleFundsCommitmentChange}
              label={t('Funds Commitment')}
            >
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
                value={selectedItems}
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
                      selectedCommitment.fundsCommitmentItems.every((item) =>
                        selectedItems.includes(item.recSerialNumber.toString()),
                      )
                    }
                    indeterminate={
                      selectedCommitment?.fundsCommitmentItems.some((item) =>
                        selectedItems.includes(item.recSerialNumber.toString()),
                      ) &&
                      !selectedCommitment.fundsCommitmentItems.every((item) =>
                        selectedItems.includes(item.recSerialNumber.toString()),
                      )
                    }
                    onChange={handleItemsChange}
                  />
                  <ListItemText primary={t('Select All')} />
                </MenuItem>
                {selectedCommitment.fundsCommitmentItems.map((item) => (
                  <MenuItem
                    key={item.recSerialNumber}
                    value={item.recSerialNumber}
                  >
                    <Checkbox
                      checked={selectedItems.includes(
                        item.recSerialNumber.toString(),
                      )}
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
          <Tooltip title={!canAssignFunds ? t('Permission Denied') : ''} arrow>
            <span>
              <LoadingButton
                variant="contained"
                loading={loadingAssign}
                color="primary"
                onClick={handleSubmit}
                disabled={
                  !canAssignFunds ||
                  !selectedFundsCommitment ||
                  selectedItems.length === 0
                }
              >
                {t('Assign Funds Commitments')}
              </LoadingButton>
            </span>
          </Tooltip>
        </Box>
      </ContainerColumnWithBorder>
    </Box>
  );
};

export default FundsCommitmentSection;
