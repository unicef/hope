import React, { useState } from 'react';
import { Formik, Form, Field } from 'formik';
import styled from 'styled-components';
import {
  Button,
  DialogContent,
  DialogTitle,
  Tabs,
  Tab,
  Typography,
  Box,
} from '@material-ui/core';
import CheckRoundedIcon from '@material-ui/icons/CheckRounded';

import { useSnackbar } from '../../hooks/useSnackBar';
import { Dialog } from '../../containers/dialogs/Dialog';
import { DialogActions } from '../../containers/dialogs/DialogActions';
import { TabPanel } from '../TabPanel';
import { FormikSliderField } from '../../shared/Formik/FormikSliderField';
import { FormikCheckboxField } from '../../shared/Formik/FormikCheckboxField';
import { FormikMultiSelectField } from '../../shared/Formik/FormikMultiSelectField/FormikMultiSelectField';

const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
`;

const DialogDescription = styled.div`
  margin: 20px 0;
  font-size: 14px;
  color: rgba(0, 0, 0, 0.54);
`;

const StyledTabs = styled(Tabs)`
  && {
    max-width: 500px;
  }
`;
const TabsContainer = styled.div`
  border-bottom: 1px solid #e8e8e8;
`;
const DialogContainer = styled.div`
  width: 700px;
`;

export function NewPaymentVerificationDialog(): React.ReactElement {
  const [open, setOpen] = useState(false);
  const [selectedTab, setSelectedTab] = useState(0);

  const { showMessage } = useSnackbar();

  // const submit = async (): Promise<void> => {
  //   // const { errors } = await mutate();
  //   const errors = [];
  //   if (errors) {
  //     showMessage('Error while submitting');
  //     return;
  //   }
  //   showMessage('New verification plan created.');
  // };

  const options = [
    {
      value: 1,
      name: 'Oliver Hansen',
    },
    {
      value: 2,
      name: 'Van Henry',
    },
    {
      value: 3,
      name: 'April Tucker',
    },
    {
      value: 4,
      name: 'John James',
    },
    {
      value: 5,
      name: 'Jimmy Choo',
    },
    {
      value: 6,
      name: 'John Polasky',
    },
    {
      value: 7,
      name: 'Chris Cross',
    },
    {
      value: 8,
      name: 'Arthur Schwartz',
    },
    {
      value: 9,
      name: 'Bridget Hansen',
    },
    {
      value: 10,
      name: 'CJ Will',
    },
  ];

  const initialValues = {
    confidenceInterval: 8,
    marginOfError: 24,
    admin: false,
    age: true,
    sex: false,
    filterAdminAreas: [],
  };

  return (
    <Formik
      initialValues={initialValues}
      onSubmit={(values) => {
        console.log(values);
      }}
    >
      {({ submitForm, values }) => (
        <Form>
          <Button
            color='primary'
            variant='contained'
            onClick={() => setOpen(true)}
            data-cy='button-new-plan'
          >
            NEW VERIFICATION PLAN
          </Button>
          <Dialog
            open={open}
            onClose={() => setOpen(false)}
            scroll='paper'
            aria-labelledby='form-dialog-title'
          >
            <DialogTitleWrapper>
              <DialogTitle id='scroll-dialog-title'>
                Create Verification Plan
              </DialogTitle>
            </DialogTitleWrapper>
            <DialogContent>
              <DialogContainer>
                {/* <DialogDescription>
            <div>description part</div>
          </DialogDescription> */}
                <TabsContainer>
                  <StyledTabs
                    value={selectedTab}
                    onChange={(
                      event: React.ChangeEvent<{}>,
                      newValue: number,
                    ) => setSelectedTab(newValue)}
                    indicatorColor='primary'
                    textColor='primary'
                    variant='fullWidth'
                    aria-label='full width tabs example'
                  >
                    <Tab label='FULL LIST' />
                    <Tab label='RANDOM SAMPLING' />
                  </StyledTabs>
                </TabsContainer>
                <TabPanel value={selectedTab} index={0}>
                  <div>full list here</div>
                </TabPanel>
                <TabPanel value={selectedTab} index={1}>
                  <Box pt={3}>
                    <Field
                      name='confidenceInterval'
                      label='Confidence Interval'
                      component={FormikSliderField}
                    />
                    <Field
                      name='marginOfError'
                      label='Margin of Error'
                      component={FormikSliderField}
                    />
                    <Typography variant='caption'>Cluster Filters</Typography>
                    <Box display='flex'>
                      <Field
                        name='admin'
                        label='Admin'
                        color='primary'
                        component={FormikCheckboxField}
                      />
                      <Field
                        name='age'
                        label='Age'
                        color='primary'
                        component={FormikCheckboxField}
                      />
                      <Field
                        name='sex'
                        label='Sex'
                        color='primary'
                        component={FormikCheckboxField}
                      />
                    </Box>
                    <Field
                      name='filterAdminAreas'
                      options={options}
                      label='Filter Out Admin Areas'
                      component={FormikMultiSelectField}
                    />
                  </Box>
                </TabPanel>
              </DialogContainer>
            </DialogContent>
            <DialogFooter>
              <DialogActions>
                <Button onClick={() => setOpen(false)}>CANCEL</Button>
                <Button
                  startIcon={<CheckRoundedIcon />}
                  type='submit'
                  color='primary'
                  variant='contained'
                  onClick={submitForm}
                  data-cy='button-submit'
                >
                  SAVE
                </Button>
              </DialogActions>
            </DialogFooter>
          </Dialog>
        </Form>
      )}
    </Formik>
  );
}
