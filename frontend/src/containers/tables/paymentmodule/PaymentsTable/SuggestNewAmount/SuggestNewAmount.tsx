import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  Grid,
} from '@material-ui/core';
import { Field, Formik } from 'formik';
import React, { Dispatch, SetStateAction } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';

import { LabelizedField } from '../../../../../components/core/LabelizedField';
import { Missing } from '../../../../../components/core/Missing';
import { FormikTextField } from '../../../../../shared/Formik/FormikTextField';
import { DialogFooter } from '../../../../dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../../../dialogs/DialogTitleWrapper';

export const StyledLink = styled.div`
  color: #000;
  text-decoration: underline;
  cursor: pointer;
  display: flex;
  align-content: center;
`;

const GreyBox = styled(Box)`
  background-color: #f3f3f3;
  min-width: 500px;
`;

const StyledDialogContent = styled(DialogContent)`
  z-index: 9999;
`;

interface SuggestNewAmountProps {
  businessArea: string;
  dialogOpen: boolean;
  setDialogOpen: Dispatch<SetStateAction<boolean>>;
}

export const SuggestNewAmount = ({
  businessArea,
  dialogOpen,
  setDialogOpen,
}: SuggestNewAmountProps): React.ReactElement => {
  const { t } = useTranslation();
  const initialValues = {
    comment: '',
    proposedAmount: '',
  };

  const handleDialogOpen = (e): void => {
    e.stopPropagation();
    setDialogOpen(true);
  };

  return (
    <Formik
      initialValues={initialValues}
      onSubmit={(values) => {
        console.log(values);
      }}
    >
      {({ submitForm, setFieldValue }) => (
        <Dialog
          open={dialogOpen}
          onClose={() => setDialogOpen(false)}
          scroll='paper'
          aria-labelledby='form-dialog-title'
          maxWidth='lg'
        >
          <DialogTitleWrapper>
            <DialogTitle id='scroll-dialog-title'>
              {t('Suggest New Amount')}
            </DialogTitle>
          </DialogTitleWrapper>
          <StyledDialogContent>
            <GreyBox mt={4} p={3}>
              <Grid container>
                <Grid item xs={6}>
                  <LabelizedField
                    label={t('Household Id')}
                    value={<Missing />}
                  />
                </Grid>
                <Grid item xs={6}>
                  <LabelizedField
                    label={t('Head of Household')}
                    value={<Missing />}
                  />
                </Grid>
              </Grid>
            </GreyBox>
            <Box mt={4}>
              <LabelizedField label={t('Current Amount')} value={<Missing />} />
            </Box>
            <Box mt={4}>
              <Grid container>
                <Grid item xs={6}>
                  <Field
                    name='proposedAmount'
                    type='number'
                    label={t('Proposed Amount')}
                    color='primary'
                    component={FormikTextField}
                    variant='outlined'
                    fullWidth
                  />
                </Grid>
                <Grid item xs={6} />
                <Grid item xs={12}>
                  <Box mt={4}>
                    <Divider />
                  </Box>
                  <Box mt={4}>
                    <Field
                      name='comment'
                      label={t('Comment (Optional)')}
                      color='primary'
                      component={FormikTextField}
                      variant='outlined'
                      multiline
                      rows={6}
                      fullWidth
                    />
                  </Box>
                </Grid>
              </Grid>
            </Box>
          </StyledDialogContent>
          <DialogFooter>
            <DialogActions>
              <Button
                onClick={(e) => {
                  e.stopPropagation();
                  setDialogOpen(false);
                }}
              >
                {t('CANCEL')}
              </Button>
              <Button
                type='submit'
                color='primary'
                variant='contained'
                onClick={submitForm}
              >
                {t('SAVE')}
              </Button>
            </DialogActions>
          </DialogFooter>
        </Dialog>
      )}
    </Formik>
  );
};
