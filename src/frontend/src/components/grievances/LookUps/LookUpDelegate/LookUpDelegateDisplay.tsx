import { Box, Grid } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import { useTranslation } from 'react-i18next';
import { BlueText, DarkGrey, LightGrey, StyledBox } from '../LookUpStyles';
import { ReactElement } from 'react';

interface LookUpDelegateDisplayProps {
  values;
  setLookUpDialogOpen: (open: boolean) => void;
  onValueChange;
  disabled?: boolean;
}

export const LookUpDelegateDisplay = ({
  values,
  setLookUpDialogOpen,
  onValueChange,
  disabled = false,
}: LookUpDelegateDisplayProps): ReactElement => {
  const { t } = useTranslation();

  const handleRemove = (): void => {
    onValueChange('selectedDelegate', null);
  };

  return (
    <StyledBox disabled={disabled}>
      <Grid container>
        <Grid>
          <Box display="flex" flexDirection="column">
            {t('Delegate')}:
            <BlueText data-cy="delegate-individual">
              {values.selectedDelegate?.unicefId ||
                values.selectedDelegate?.fullName ||
                '-'}
            </BlueText>
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
