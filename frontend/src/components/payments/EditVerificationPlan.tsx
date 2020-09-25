import React, { useState, useEffect } from 'react';
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
  Grid,
} from '@material-ui/core';
import { useSnackbar } from '../../hooks/useSnackBar';
import { Dialog } from '../../containers/dialogs/Dialog';
import { DialogActions } from '../../containers/dialogs/DialogActions';
import { TabPanel } from '../TabPanel';
import { FormikSliderField } from '../../shared/Formik/FormikSliderField';
import { FormikRadioGroup } from '../../shared/Formik/FormikRadioGroup';
import {
  useAllRapidProFlowsQuery,
  useAllAdminAreasQuery,
  useSampleSizeQuery,
  useEditCashPlanPaymentVerificationMutation,
  useCashPlanQuery,
} from '../../__generated__/graphql';
import { FormikMultiSelectField } from '../../shared/Formik/FormikMultiSelectField';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { FormikSelectField } from '../../shared/Formik/FormikSelectField';
import { FormikTextField } from '../../shared/Formik/FormikTextField';
import { FormikEffect } from '../FormikEffect';
import { CashPlan } from '../../apollo/queries/CashPlan';
import { FormikCheckboxField } from '../../shared/Formik/FormikCheckboxField';

const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
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

export interface Props {
  cashPlanVerificationId: string;
  cashPlanId: string;
}
export function EditVerificationPlan({
  cashPlanVerificationId,
  cashPlanId,
}: Props): React.ReactElement {
  const [open, setOpen] = useState(false);
  const [selectedTab, setSelectedTab] = useState(0);
  const { showMessage } = useSnackbar();
  const [mutate] = useEditCashPlanPaymentVerificationMutation();
  const businessArea = useBusinessArea();
  const {
    data: { cashPlan },
  } = useCashPlanQuery({
    variables: { id: cashPlanId },
  });
  const verification = cashPlan?.verifications?.edges[0].node;
  useEffect(() => {
    if (verification.sampling === 'FULL_LIST') {
      setSelectedTab(0);
    } else {
      setSelectedTab(1);
    }
  }, [verification.sampling]);

  const initialValues = {
    confidenceInterval: verification.confidenceInterval * 100 || 1,
    marginOfError: verification.marginOfError * 100 || 1,
    filterAgeMin: verification.ageFilter?.min || 0,
    filterAgeMax: verification.ageFilter?.max || 0,
    filterSex: verification.sexFilter || '',
    excludedAdminAreasFull: verification.excludedAdminAreasFilter,
    excludedAdminAreasRandom: verification.excludedAdminAreasFilter,
    verificationChannel: verification.verificationMethod || null,
    rapidProFlow: verification.rapidProFlowId || null,
    adminCheckbox: Boolean(verification.excludedAdminAreasFilter) || false,
    ageCheckbox: Boolean(verification.ageFilter?.min) || false,
    sexCheckbox: Boolean(verification.sexFilter) || false,
  };

  const [formValues, setFormValues] = useState(initialValues);

  const { data: rapidProFlows } = useAllRapidProFlowsQuery({
    variables: {
      businessAreaSlug: businessArea,
    },
  });
  const { data } = useAllAdminAreasQuery({
    variables: {
      first: 100,
      businessArea,
    },
  });

  const { data: sampleSizesData, refetch } = useSampleSizeQuery({
    variables: {
      input: {
        cashPlanId,
        sampling: selectedTab === 0 ? 'FULL_LIST' : 'RANDOM',
        businessAreaSlug: businessArea,
        fullListArguments:
          selectedTab === 0
            ? {
                excludedAdminAreas: formValues.excludedAdminAreasFull,
              }
            : null,
        randomSamplingArguments:
          selectedTab === 1
            ? {
                confidenceInterval: Number(
                  (formValues.confidenceInterval * 0.01).toFixed(2),
                ),
                marginOfError: formValues.marginOfError * 0.01,
                excludedAdminAreas: formValues.excludedAdminAreasRandom,
                age: {
                  min: formValues.filterAgeMin || null,
                  max: formValues.filterAgeMax || null,
                },
                sex: formValues.filterSex,
              }
            : null,
      },
    },
  });

  useEffect(() => {
    if (formValues) {
      refetch();
    }
  }, [refetch, formValues, sampleSizesData]);

  const submit = async (values): Promise<void> => {
    const { errors } = await mutate({
      variables: {
        input: {
          cashPlanPaymentVerificationId: cashPlanVerificationId,
          sampling: selectedTab === 0 ? 'FULL_LIST' : 'RANDOM',
          fullListArguments:
            selectedTab === 0
              ? {
                  excludedAdminAreas: values.excludedAdminAreasFull || [],
                }
              : null,
          verificationChannel: values.verificationChannel,
          rapidProArguments:
            values.verificationChannel === 'RAPIDPRO'
              ? {
                  flowId: values.rapidProFlow,
                }
              : null,
          randomSamplingArguments:
            selectedTab === 1
              ? {
                  confidenceInterval: values.confidenceInterval * 0.01,
                  marginOfError: values.marginOfError * 0.01,
                  excludedAdminAreas: values.adminCheckbox
                    ? values.excludedAdminAreasRandom
                    : [],
                  age: values.ageCheckbox
                    ? { min: values.filterAgeMin, max: values.filterAgeMax }
                    : null,
                  sex: values.sexCheckbox ? values.filterSex : null,
                }
              : null,
          businessAreaSlug: businessArea,
        },
      },
      refetchQueries: () => [
        { query: CashPlan, variables: { id: cashPlanId } },
      ],
    });
    setOpen(false);

    if (errors) {
      showMessage('Error while submitting');
      return;
    }
    showMessage('Verification plan edited.');
  };

  const mappedAdminAreas = data?.allAdminAreas?.edges?.length
    ? data.allAdminAreas.edges.map((el) => ({
        value: el.node.id,
        name: el.node.title,
      }))
    : [];

  const handleFormChange = (values): void => {
    setFormValues(values);
  };

  const getSampleSizePercentage = (): string => {
    if (sampleSizesData?.sampleSize?.paymentRecordCount !== 0) {
      return ` (${(sampleSizesData?.sampleSize?.sampleSize /
        sampleSizesData?.sampleSize?.paymentRecordCount) *
        100})%`;
    }
    return ` (0%)`;
  };
  return (
    <Formik initialValues={initialValues} onSubmit={submit}>
      {({ submitForm, values, setValues }) => (
        <Form>
          <FormikEffect values={values} onChange={handleFormChange(values)} />
          <Button
            color='primary'
            variant='contained'
            onClick={() => setOpen(true)}
            data-cy='button-new-plan'
          >
            EDIT VERIFICATION PLAN
          </Button>
          <Dialog
            open={open}
            onClose={() => setOpen(false)}
            scroll='paper'
            aria-labelledby='form-dialog-title'
          >
            <DialogTitleWrapper>
              <DialogTitle id='scroll-dialog-title'>
                Edit Verification Plan
              </DialogTitle>
            </DialogTitleWrapper>
            <DialogContent>
              <DialogContainer>
                <TabsContainer>
                  <StyledTabs
                    value={selectedTab}
                    onChange={(
                      event: React.ChangeEvent<{}>,
                      newValue: number,
                    ) => {
                      setValues(initialValues);
                      setFormValues(initialValues);
                      setSelectedTab(newValue);
                    }}
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
                  {mappedAdminAreas && (
                    <Field
                      name='excludedAdminAreasFull'
                      choices={mappedAdminAreas}
                      variant='outlined'
                      label='Filter Out Administrative Level Areas'
                      component={FormikMultiSelectField}
                    />
                  )}
                  <Box pt={3}>
                    <Box
                      pb={3}
                      pt={3}
                      fontSize={16}
                      fontWeight='fontWeightBold'
                    >
                      Sample size: {sampleSizesData?.sampleSize?.sampleSize} out
                      of {sampleSizesData?.sampleSize?.paymentRecordCount}
                      {getSampleSizePercentage()}
                    </Box>
                    <Field
                      name='verificationChannel'
                      label='Verification Channel'
                      style={{ flexDirection: 'row' }}
                      choices={[
                        { value: 'RAPIDPRO', name: 'RAPIDPRO' },
                        { value: 'XLSX', name: 'XLSX' },
                        { value: 'MANUAL', name: 'MANUAL' },
                      ]}
                      component={FormikRadioGroup}
                    />
                    {values.verificationChannel === 'RAPIDPRO' && (
                      <Field
                        name='rapidProFlow'
                        label='RapidPro Flow'
                        style={{ width: '90%' }}
                        choices={
                          rapidProFlows
                            ? rapidProFlows.allRapidProFlows.map((flow) => ({
                                value: flow.id,
                                name: flow.name,
                              }))
                            : []
                        }
                        component={FormikSelectField}
                      />
                    )}
                  </Box>
                </TabPanel>
                <TabPanel value={selectedTab} index={1}>
                  <Box pt={3}>
                    <Field
                      name='confidenceInterval'
                      label='Confidence Interval'
                      min={1}
                      max={99}
                      component={FormikSliderField}
                      suffix='%'
                    />
                    <Field
                      name='marginOfError'
                      label='Margin of Error'
                      min={1}
                      max={10}
                      component={FormikSliderField}
                      suffix='%'
                    />
                    <Typography variant='caption'>Cluster Filters</Typography>
                    <Box flexDirection='column' display='flex'>
                      <Box display='flex'>
                        <Field
                          name='adminCheckbox'
                          label='Administrative Level'
                          component={FormikCheckboxField}
                        />
                        <Field
                          name='ageCheckbox'
                          label='Age'
                          component={FormikCheckboxField}
                        />
                        <Field
                          name='sexCheckbox'
                          label='Gender'
                          component={FormikCheckboxField}
                        />
                      </Box>
                      {values.adminCheckbox && (
                        <Field
                          name='excludedAdminAreasRandom'
                          choices={mappedAdminAreas}
                          variant='outlined'
                          label='Filter Out Administrative Level Areas'
                          component={FormikMultiSelectField}
                        />
                      )}

                      <Grid container>
                        {values.ageCheckbox && (
                          <Grid item xs={12}>
                            <Grid container>
                              <Grid item xs={4}>
                                <Field
                                  name='filterAgeMin'
                                  label='Age Min'
                                  type='number'
                                  color='primary'
                                  component={FormikTextField}
                                />
                              </Grid>
                              <Grid item xs={4}>
                                <Field
                                  name='filterAgeMax'
                                  label='Age Max'
                                  type='number'
                                  color='primary'
                                  component={FormikTextField}
                                />
                              </Grid>
                            </Grid>
                          </Grid>
                        )}
                        {values.sexCheckbox && (
                          <Grid item xs={5}>
                            <Field
                              name='filterSex'
                              label='Gender'
                              color='primary'
                              choices={[
                                { value: 'FEMALE', name: 'Female' },
                                { value: 'MALE', name: 'Male' },
                              ]}
                              component={FormikSelectField}
                            />
                          </Grid>
                        )}
                      </Grid>
                    </Box>

                    <Box
                      pb={3}
                      pt={3}
                      fontSize={16}
                      fontWeight='fontWeightBold'
                    >
                      Sample size: {sampleSizesData?.sampleSize?.sampleSize} out
                      of {sampleSizesData?.sampleSize?.paymentRecordCount} (
                      {(sampleSizesData?.sampleSize?.sampleSize /
                        sampleSizesData?.sampleSize?.paymentRecordCount) *
                        100}
                      %)
                    </Box>
                    <Field
                      name='verificationChannel'
                      label='Verification Channel'
                      style={{ flexDirection: 'row' }}
                      choices={[
                        { value: 'RAPIDPRO', name: 'RAPIDPRO' },
                        { value: 'XLSX', name: 'XLSX' },
                        { value: 'MANUAL', name: 'MANUAL' },
                      ]}
                      component={FormikRadioGroup}
                    />
                    {values.verificationChannel === 'RAPIDPRO' && (
                      <Field
                        name='rapidProFlow'
                        label='RapidPro Flow'
                        style={{ width: '90%' }}
                        choices={
                          rapidProFlows ? rapidProFlows.allRapidProFlows : []
                        }
                        component={FormikSelectField}
                      />
                    )}
                  </Box>
                </TabPanel>
              </DialogContainer>
            </DialogContent>
            <DialogFooter>
              <DialogActions>
                <Button onClick={() => setOpen(false)}>CANCEL</Button>
                <Button
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
