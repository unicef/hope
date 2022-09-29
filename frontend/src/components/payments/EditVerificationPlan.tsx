import {
  Box,
  Button,
  DialogContent,
  DialogTitle,
  Grid,
  Tab,
  Tabs,
  Typography,
} from '@material-ui/core';
import EditIcon from '@material-ui/icons/EditRounded';
import { Field, Form, Formik } from 'formik';
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { Dialog } from '../../containers/dialogs/Dialog';
import { DialogActions } from '../../containers/dialogs/DialogActions';
import { DialogContainer } from '../../containers/dialogs/DialogContainer';
import { DialogFooter } from '../../containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../containers/dialogs/DialogTitleWrapper';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { usePaymentRefetchQueries } from '../../hooks/usePaymentRefetchQueries';
import { useSnackbar } from '../../hooks/useSnackBar';
import { FormikCheckboxField } from '../../shared/Formik/FormikCheckboxField';
import { FormikMultiSelectField } from '../../shared/Formik/FormikMultiSelectField';
import { FormikRadioGroup } from '../../shared/Formik/FormikRadioGroup';
import { FormikSelectField } from '../../shared/Formik/FormikSelectField';
import { FormikSliderField } from '../../shared/Formik/FormikSliderField';
import { FormikTextField } from '../../shared/Formik/FormikTextField';
import {
  useAllAdminAreasQuery,
  useAllRapidProFlowsQuery,
  useCashPlanQuery,
  useEditCashPlanPaymentVerificationMutation,
  useSampleSizeLazyQuery,
} from '../../__generated__/graphql';
import { FormikEffect } from '../core/FormikEffect';
import { LoadingButton } from '../core/LoadingButton';
import { TabPanel } from '../core/TabPanel';

const StyledTabs = styled(Tabs)`
  && {
    max-width: 500px;
  }
`;
const TabsContainer = styled.div`
  border-bottom: 1px solid #e8e8e8;
`;

// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
function prepareVariables(
  paymentVerificationPlanId,
  selectedTab,
  values,
  businessArea,
  cashPlanId = null,
) {
  return {
    input: {
      ...(paymentVerificationPlanId && {
        paymentVerificationPlanId,
      }),
      ...(cashPlanId && { cashPlanId }),
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
                ? {
                    min: values.filterAgeMin || null,
                    max: values.filterAgeMax || null,
                  }
                : null,
              sex: values.sexCheckbox ? values.filterSex : null,
            }
          : null,
      businessAreaSlug: businessArea,
    },
  };
}

export interface Props {
  paymentVerificationPlanId: string;
  cashPlanId: string;
}
export function EditVerificationPlan({
  paymentVerificationPlanId,
  cashPlanId,
}: Props): React.ReactElement {
  const refetchQueries = usePaymentRefetchQueries(cashPlanId);
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [selectedTab, setSelectedTab] = useState(0);
  const { showMessage } = useSnackbar();
  const [mutate, { loading }] = useEditCashPlanPaymentVerificationMutation();
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
    confidenceInterval: verification.confidenceInterval * 100 || 95,
    marginOfError: verification.marginOfError * 100 || 5,
    filterAgeMin: verification.ageFilter?.min || '',
    filterAgeMax: verification.ageFilter?.max || '',
    filterSex: verification.sexFilter || '',
    excludedAdminAreasFull: verification.excludedAdminAreasFilter,
    excludedAdminAreasRandom: verification.excludedAdminAreasFilter,
    verificationChannel: verification.verificationChannel || null,
    rapidProFlow: verification.rapidProFlowId || null,
    adminCheckbox: verification.excludedAdminAreasFilter.length !== 0,
    ageCheckbox:
      Boolean(verification.ageFilter?.min) ||
      Boolean(verification.ageFilter?.max) ||
      false,
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

  const [loadSampleSize, { data: sampleSizesData }] = useSampleSizeLazyQuery({
    variables: prepareVariables(
      paymentVerificationPlanId,
      selectedTab,
      formValues,
      businessArea,
      cashPlanId,
    ),
    fetchPolicy: 'network-only',
  });

  useEffect(() => {
    loadSampleSize();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [formValues, open]);

  const submit = async (values): Promise<void> => {
    const { errors } = await mutate({
      variables: prepareVariables(
        paymentVerificationPlanId,
        selectedTab,
        values,
        businessArea,
      ),
      refetchQueries,
    });
    setOpen(false);

    if (errors) {
      showMessage(t('Error while submitting'));
      return;
    }
    showMessage(t('Verification plan edited.'));
  };

  const mappedAdminAreas = data?.allAdminAreas?.edges?.length
    ? data.allAdminAreas.edges.map((el) => ({
        value: el.node.id,
        name: el.node.name,
      }))
    : [];

  const handleFormChange = (values): void => {
    setFormValues(values);
  };

  const getSampleSizePercentage = (): string => {
    if (sampleSizesData?.sampleSize?.paymentRecordCount !== 0) {
      return ` (${
        (sampleSizesData?.sampleSize?.sampleSize /
          sampleSizesData?.sampleSize?.paymentRecordCount) *
        100
      })%`;
    }
    return ` (0%)`;
  };
  return (
    <Formik initialValues={initialValues} onSubmit={submit}>
      {({ submitForm, values, setValues }) => (
        <Form>
          <FormikEffect
            values={values}
            onChange={() => handleFormChange(values)}
          />
          <Button
            color='primary'
            onClick={() => setOpen(true)}
            startIcon={<EditIcon />}
            data-cy='button-new-plan'
          >
            {t('Edit')}
          </Button>
          <Dialog
            open={open}
            onClose={() => setOpen(false)}
            scroll='paper'
            aria-labelledby='form-dialog-title'
            maxWidth='md'
          >
            <DialogTitleWrapper>
              <DialogTitle id='scroll-dialog-title'>
                {t('Edit Verification Plan')}
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
                    <Tab label={t('FULL LIST')} />
                    <Tab label={t('RANDOM SAMPLING')} />
                  </StyledTabs>
                </TabsContainer>
                <TabPanel value={selectedTab} index={0}>
                  {mappedAdminAreas && (
                    <Field
                      name='excludedAdminAreasFull'
                      choices={mappedAdminAreas}
                      variant='outlined'
                      label={t('Filter Out Administrative Level Areas')}
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
                    <Box fontSize={12} color='#797979'>
                      {t('This option is recommended for RapidPro')}
                    </Box>
                    <Field
                      name='verificationChannel'
                      label={t('Verification Channel')}
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
                      label={t('Confidence Interval')}
                      min={90}
                      max={99}
                      component={FormikSliderField}
                      suffix='%'
                    />
                    <Field
                      name='marginOfError'
                      label={t('Margin of Error')}
                      min={0}
                      max={9}
                      component={FormikSliderField}
                      suffix='%'
                    />
                    <Typography variant='caption'>
                      {t('Cluster Filters')}
                    </Typography>
                    <Box flexDirection='column' display='flex'>
                      <Box display='flex'>
                        <Field
                          name='adminCheckbox'
                          label={t('Administrative Level')}
                          component={FormikCheckboxField}
                        />
                        <Field
                          name='ageCheckbox'
                          label={t('Age of HoH')}
                          component={FormikCheckboxField}
                        />
                        <Field
                          name='sexCheckbox'
                          label={t('Gender of HoH')}
                          component={FormikCheckboxField}
                        />
                      </Box>
                      {values.adminCheckbox && (
                        <Field
                          name='excludedAdminAreasRandom'
                          choices={mappedAdminAreas}
                          variant='outlined'
                          label={t('Filter Out Administrative Level Areas')}
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
                                  label={t('Minimum Age')}
                                  type='number'
                                  color='primary'
                                  component={FormikTextField}
                                />
                              </Grid>
                              <Grid item xs={4}>
                                <Field
                                  name='filterAgeMax'
                                  label={t('Maximum Age')}
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
                              label={t('Gender')}
                              color='primary'
                              choices={[
                                { value: 'FEMALE', name: t('Female') },
                                { value: 'MALE', name: t('Male') },
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
                      of {sampleSizesData?.sampleSize?.paymentRecordCount}{' '}
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
                <Button onClick={() => setOpen(false)}>{t('CANCEL')}</Button>
                <LoadingButton
                  loading={loading}
                  type='submit'
                  color='primary'
                  variant='contained'
                  onClick={submitForm}
                  data-cy='button-submit'
                >
                  {t('SAVE')}
                </LoadingButton>
              </DialogActions>
            </DialogFooter>
          </Dialog>
        </Form>
      )}
    </Formik>
  );
}
