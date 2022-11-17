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
import { getPercentage } from '../../utils/utils';
import {
  useAllAdminAreasQuery,
  useAllRapidProFlowsQuery,
  useCreatePaymentVerificationPlanMutation,
  useSampleSizeLazyQuery,
} from '../../__generated__/graphql';
import { AutoSubmitFormOnEnter } from '../core/AutoSubmitFormOnEnter';
import { ButtonTooltip } from '../core/ButtonTooltip';
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

const initialValues = {
  confidenceInterval: 95,
  marginOfError: 5,
  filterAgeMin: null,
  filterAgeMax: null,
  filterSex: '',
  excludedAdminAreasFull: [],
  excludedAdminAreasRandom: [],
  verificationChannel: 'MANUAL',
  rapidProFlow: '',
  adminCheckbox: false,
  ageCheckbox: false,
  sexCheckbox: false,
};

// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
function prepareVariables(cashOrPaymentPlanId, selectedTab, values, businessArea) {
  const variables = {
    input: {
      cashOrPaymentPlanId,
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
  };
  return variables;
}

export interface Props {
  cashOrPaymentPlanId: string;
  disabled: boolean;
  canCreatePaymentVerificationPlan: boolean;
}
export function CreateVerificationPlan({
  cashOrPaymentPlanId,
  disabled,
  canCreatePaymentVerificationPlan,
}: Props): React.ReactElement {
  const refetchQueries = usePaymentRefetchQueries(cashOrPaymentPlanId);
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [selectedTab, setSelectedTab] = useState(0);
  const { showMessage } = useSnackbar();
  const [mutate, { loading }] = useCreatePaymentVerificationPlanMutation();
  const businessArea = useBusinessArea();
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
      cashOrPaymentPlanId,
      selectedTab,
      formValues,
      businessArea,
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
        cashOrPaymentPlanId,
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
    showMessage(t('New verification plan created.'));
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
    return `(${getPercentage(
      sampleSizesData?.sampleSize?.sampleSize,
      sampleSizesData?.sampleSize?.paymentRecordCount,
    )})`;
  };

  const handleOpen = (): void => {
    if (canCreatePaymentVerificationPlan) {
      setOpen(true);
    } else {
      showMessage(
        t(
          'There are no payment records that could be assigned to a new verification plan.',
        ),
      );
    }
  };

  return (
    <Formik initialValues={initialValues} onSubmit={submit}>
      {({ submitForm, values, setValues }) => (
        <Form>
          <AutoSubmitFormOnEnter />
          <FormikEffect
            values={values}
            onChange={() => handleFormChange(values)}
          />
          <Box mr={2}>
            <ButtonTooltip
              disabled={disabled}
              color='primary'
              variant='contained'
              onClick={() => handleOpen()}
              data-cy='button-new-plan'
            >
              {t('CREATE VERIFICATION PLAN')}
            </ButtonTooltip>
          </Box>
          <Dialog
            open={open}
            onClose={() => setOpen(false)}
            scroll='paper'
            aria-labelledby='form-dialog-title'
            maxWidth='md'
          >
            <DialogTitleWrapper>
              <DialogTitle id='scroll-dialog-title'>
                {t('Create Verification Plan')}
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
                      of {sampleSizesData?.sampleSize?.paymentRecordCount}{' '}
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
                        label={t('RapidPro Flow')}
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
                      of {sampleSizesData?.sampleSize?.paymentRecordCount}
                      {getSampleSizePercentage()}
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
              </DialogContainer>
            </DialogContent>
            <DialogFooter>
              <DialogActions>
                <Button onClick={() => setOpen(false)}>CANCEL</Button>
                <LoadingButton
                  loading={loading}
                  type='submit'
                  color='primary'
                  variant='contained'
                  onClick={submitForm}
                  data-cy='button-submit'
                >
                  SAVE
                </LoadingButton>
              </DialogActions>
            </DialogFooter>
          </Dialog>
        </Form>
      )}
    </Formik>
  );
}
