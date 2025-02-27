import { Box, Grid2 as Grid } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import { useTranslation } from 'react-i18next';
import { BlueText, DarkGrey, LightGrey, StyledBox } from '../LookUpStyles';
import { ReactElement } from 'react';

interface LookUpPaymentRecordDisplayProps {
  values;
  setLookUpDialogOpen: (open: boolean) => void;
  onValueChange;
  disabled?: boolean;
}

export const LookUpPaymentRecordDisplay = ({
  values,
  setLookUpDialogOpen,
  onValueChange,
  disabled = false,
}: LookUpPaymentRecordDisplayProps): ReactElement => {
  const { t } = useTranslation();
  const handleRemove = (): void => {
    onValueChange('selectedPaymentRecords', []);
  };
  const renderPaymentRecords = (): ReactElement => {
    if (values.selectedPaymentRecords.length) {
      return values.selectedPaymentRecords.map((record) => (
        <BlueText key={record.id} data-cy="payment-record">
          {record.unicefId}
        </BlueText>
      ));
    }
    return <BlueText>-</BlueText>;
  };
  return (
    <StyledBox disabled={disabled}>
      <Grid container>
        <Grid>
          <Box display="flex" flexDirection="column">
            {t('Payment ID')}:{renderPaymentRecords()}
          </Box>
        </Grid>
        {disabled || (
          <Grid>
            <Box p={2}>
              <Grid container justifyContent="center" alignItems="center">
                <Grid>
                  <LightGrey>
                    <EditIcon
                      color="inherit"
                      fontSize="small"
                      onClick={() => setLookUpDialogOpen(true)}
                    />
                  </LightGrey>
                </Grid>
                <Grid>
                  <DarkGrey>
                    <DeleteIcon
                      color="inherit"
                      fontSize="small"
                      onClick={() => handleRemove()}
                    />
                  </DarkGrey>
                </Grid>
              </Grid>
            </Box>
          </Grid>
        )}
      </Grid>
    </StyledBox>
  );
};
