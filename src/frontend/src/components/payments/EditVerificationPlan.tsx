import {
  Box,
  Button,
  DialogContent,
  DialogTitle,
  Grid2 as Grid,
  Typography,
} from '@mui/material';
import EditIcon from '@mui/icons-material/EditRounded';
import { Field, Form, Formik } from 'formik';
import { ChangeEvent, ReactElement, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';
import {
  useAllRapidProFlowsLazyQuery,
  useEditPaymentVerificationPlanMutation,
  useSampleSizeLazyQuery,
} from '@generated/graphql';
import { Dialog } from '@containers/dialogs/Dialog';
import { DialogActions } from '@containers/dialogs/DialogActions';
import { DialogContainer } from '@containers/dialogs/DialogContainer';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePaymentRefetchQueries } from '@hooks/usePaymentRefetchQueries';
import { useSnackbar } from '@hooks/useSnackBar';
import { useProgramContext } from '../../programContext';
import { FormikCheckboxField } from '@shared/Formik/FormikCheckboxField';
import { FormikMultiSelectField } from '@shared/Formik/FormikMultiSelectField';
import { FormikRadioGroup } from '@shared/Formik/FormikRadioGroup';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { FormikSliderField } from '@shared/Formik/FormikSliderField';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { AutoSubmitFormOnEnter } from '@core/AutoSubmitFormOnEnter';
import { Tabs, Tab } from '@core/Tabs';
import { FormikEffect } from '@core/FormikEffect';
import { LoadingButton } from '@core/LoadingButton';
import { TabPanel } from '@core/TabPanel';
import { RapidProFlowsLoader } from './RapidProFlowsLoader';
import { PaymentVerificationPlanDetails } from '@restgenerated/models/PaymentVerificationPlanDetails';
import { PaginatedAreaList } from '@restgenerated/models/PaginatedAreaList';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';

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
  cashOrPaymentPlanId: string,
  paymentVerificationPlanId: string | undefined,
  selectedTab: number,
  values,
  businessArea: string,
  shouldUseCashOrPaymentPlanId: boolean = false,
) {
  const getFullListArguments = (): { excludedAdminAreas: string[] } | null => {
    return selectedTab === 0
      ? { excludedAdminAreas: values.excludedAdminAreasFull || [] }
      : null;
  };

  const getRapidProArguments = (): { flowId: string } | null => {
    return values.verificationChannel === 'RAPIDPRO'
      ? { flowId: values.rapidProFlow || '' }
      : null;
  };

  // eslint-disable-next-line @typescript-eslint/explicit-function-return-type
  const getRandomSamplingArguments = () => {
    if (selectedTab !== 1) return null;

    const age = values.ageCheckbox
      ? {
          min: values.filterAgeMin || null,
          max: values.filterAgeMax || null,
        }
      : null;

    return {
      confidenceInterval: values.confidenceInterval! * 0.01,
      marginOfError: values.marginOfError! * 0.01,
      excludedAdminAreas: values.adminCheckbox
        ? values.excludedAdminAreasRandom || []
        : [],
      age,
      sex: values.sexCheckbox ? values.filterSex || null : null,
    };
  };

  return {
    input: {
      ...(shouldUseCashOrPaymentPlanId && {
        cashOrPaymentPlanId: cashOrPaymentPlanId,
      }),
      ...(paymentVerificationPlanId && { paymentVerificationPlanId }),
      sampling: selectedTab === 0 ? 'FULL_LIST' : 'RANDOM',
      fullListArguments: getFullListArguments(),
      verificationChannel: values.verificationChannel || '',
      rapidProArguments: getRapidProArguments(),
      randomSamplingArguments: getRandomSamplingArguments(),
      businessAreaSlug: businessArea,
    },
  };
}

export interface Props {
  paymentVerificationPlanNode: PaymentVerificationPlanDetails['paymentVerificationPlans'][number];
  cashOrPaymentPlanId: string;
}

export const EditVerificationPlan = ({
  paymentVerificationPlanNode,
  cashOrPaymentPlanId,
}: Props): ReactElement => {
  const refetchQueries = usePaymentRefetchQueries(cashOrPaymentPlanId);
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [selectedTab, setSelectedTab] = useState(0);
  const { showMessage } = useSnackbar();
  const [mutate, { loading }] = useEditPaymentVerificationPlanMutation();
  const { baseUrl, businessArea } = useBaseUrl();
  const { isActiveProgram, isSocialDctType } = useProgramContext();
  const navigate = useNavigate();
  useEffect(() => {
    if (paymentVerificationPlanNode.sampling === 'FULL_LIST') {
      setSelectedTab(0);
    } else {
      setSelectedTab(1);
    }
  }, [paymentVerificationPlanNode.sampling]);

  const initialValues = {
    confidenceInterval:
      paymentVerificationPlanNode.confidenceInterval * 100 || 95,
    marginOfError: paymentVerificationPlanNode.marginOfError * 100 || 5,
    filterAgeMin: paymentVerificationPlanNode.ageFilterMin || '',
    filterAgeMax: paymentVerificationPlanNode.ageFilterMax || '',
    filterSex: paymentVerificationPlanNode.sexFilter || '',
    excludedAdminAreasFull:
      paymentVerificationPlanNode.excludedAdminAreasFilter || [],
    excludedAdminAreasRandom:
      paymentVerificationPlanNode.excludedAdminAreasFilter || [],
    verificationChannel: paymentVerificationPlanNode.verificationChannel || '',
    rapidProFlow: paymentVerificationPlanNode.rapidProFlowId || '',
    adminCheckbox:
      paymentVerificationPlanNode.excludedAdminAreasFilter?.length !== 0,
    ageCheckbox:
      Boolean(paymentVerificationPlanNode.ageFilterMin) ||
      Boolean(paymentVerificationPlanNode.ageFilterMax) ||
      false,
    sexCheckbox: Boolean(paymentVerificationPlanNode.sexFilter) || false,
  };

  const [formValues, setFormValues] = useState(initialValues);

  const [loadRapidProFlows, { data: rapidProFlows }] =
    useAllRapidProFlowsLazyQuery({
      variables: {
        businessAreaSlug: businessArea,
      },
      fetchPolicy: 'network-only',
    });

  const { data: adminAreasData } = useQuery<PaginatedAreaList>({
    queryKey: ['adminAreas', businessArea, { areaTypeAreaLevel: 2 }],
    queryFn: async () => {
      return RestService.restAreasList({
        limit: 100,
        areaTypeAreaLevel: 2,
        search: undefined,
      });
    },
    enabled: !!businessArea,
  });

  const [loadSampleSize, { data: sampleSizesData }] = useSampleSizeLazyQuery({
    variables: prepareVariables(
      cashOrPaymentPlanId,
      paymentVerificationPlanNode.id,
      selectedTab,
      formValues,
      businessArea,
      true,
    ),
    fetchPolicy: 'network-only',
  });

  useEffect(() => {
    if (open) {
      loadSampleSize();
    }
  }, [open, loadSampleSize, loadRapidProFlows, selectedTab]);

  const submit = async (mutationVariables): Promise<void> => {
    const { errors } = await mutate({
      variables: prepareVariables(
        cashOrPaymentPlanId,
        paymentVerificationPlanNode.id,
        selectedTab,
        mutationVariables,
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

  const mappedAdminAreas = adminAreasData?.results?.length
    ? adminAreasData.results.map((area) => ({
        value: area.id,
        name: area.name || '',
      }))
    : [];

  const handleFormChange = (fValues): void => {
    setFormValues(fValues);
  };

  const getSampleSizePercentage = (): string => {
    const sampleSize = sampleSizesData?.sampleSize?.sampleSize;
    const paymentRecordCount = sampleSizesData?.sampleSize?.paymentRecordCount;

    if (
      !sampleSize ||
      !paymentRecordCount ||
      isNaN(sampleSize) ||
      isNaN(paymentRecordCount)
    ) {
      return '';
    }

    return ` (${(sampleSize / paymentRecordCount) * 100}%)`;
  };

  return (
    <Formik initialValues={initialValues} onSubmit={submit}>
      {({ submitForm, values, setValues }) => {
        // Redirect to error page if no flows available
        if (
          rapidProFlows &&
          !rapidProFlows?.allRapidProFlows?.length &&
          values.verificationChannel === 'RAPIDPRO'
        ) {
          navigate(`/error/${businessArea}`, {
            state: {
              errorMessage: t(
                'RapidPro is not set up in your country, please contact your Roll Out Focal Point',
              ),

              lastSuccessfulPage: `/${baseUrl}/payment-verification/payment-plan/${cashOrPaymentPlanId}`,
            },
          });
        }
        return (
          <Form>
            <RapidProFlowsLoader
              open={open}
              verificationChannel={values.verificationChannel}
              loadRapidProFlows={loadRapidProFlows}
            />
            <AutoSubmitFormOnEnter />
            <FormikEffect
              values={values}
              onChange={() => handleFormChange(values)}
            />
            <Button
              color="primary"
              onClick={() => setOpen(true)}
              startIcon={<EditIcon />}
              data-cy="button-edit-plan"
              disabled={!isActiveProgram}
            >
              {t('Edit')}
            </Button>
            <Dialog
              open={open}
              onClose={() => setOpen(false)}
              scroll="paper"
              aria-labelledby="form-dialog-title"
              maxWidth="md"
            >
              <DialogTitleWrapper>
                <DialogTitle>{t('Edit Verification Plan')}</DialogTitle>
              </DialogTitleWrapper>
              <DialogContent>
                <DialogContainer>
                  <TabsContainer>
                    <StyledTabs
                      value={selectedTab}
                      onChange={(
                        _event: ChangeEvent<object>,
                        newValue: number,
                      ) => {
                        setValues(initialValues);
                        setFormValues(initialValues);
                        setSelectedTab(newValue);
                      }}
                      indicatorColor="primary"
                      textColor="primary"
                      variant="fullWidth"
                      aria-label="full width tabs example"
                    >
                      <Tab data-cy="tab-full-list" label={t('FULL LIST')} />
                      <Tab
                        data-cy="tab-random-sampling"
                        label={t('RANDOM SAMPLING')}
                      />
                    </StyledTabs>
                  </TabsContainer>
                  <TabPanel value={selectedTab} index={0}>
                    <Box pt={6}>
                      {mappedAdminAreas && (
                        <Field
                          name="excludedAdminAreasFull"
                          choices={mappedAdminAreas}
                          variant="outlined"
                          label={t('Filter Out Administrative Level Areas')}
                          component={FormikMultiSelectField}
                        />
                      )}
                      <Box pt={3}>
                        <Box
                          pb={3}
                          pt={3}
                          fontSize={16}
                          fontWeight="fontWeightBold"
                        >
                          Sample size:{' '}
                          {isNaN(sampleSizesData?.sampleSize?.sampleSize)
                            ? ' 0'
                            : ` ${sampleSizesData?.sampleSize?.sampleSize}`}{' '}
                          out of{' '}
                          {isNaN(
                            sampleSizesData?.sampleSize?.paymentRecordCount,
                          )
                            ? ' 0'
                            : ` ${sampleSizesData?.sampleSize?.paymentRecordCount}`}
                          {getSampleSizePercentage()}
                        </Box>
                        <Box fontSize={12} color="#797979">
                          {t('This option is recommended for RapidPro')}
                        </Box>
                        <Field
                          name="verificationChannel"
                          label={t('Verification Channel')}
                          style={{ flexDirection: 'row', alignItems: 'center' }}
                          choices={[
                            {
                              value: 'RAPIDPRO',
                              name: 'RAPIDPRO',
                              dataCy: 'radio-rapidpro',
                            },
                            {
                              value: 'XLSX',
                              name: 'XLSX',
                              dataCy: 'radio-xlsx',
                            },
                            {
                              value: 'MANUAL',
                              name: 'MANUAL',
                              dataCy: 'radio-manual',
                            },
                          ]}
                          component={FormikRadioGroup}
                          alignItems="center"
                        />
                        {values.verificationChannel === 'RAPIDPRO' && (
                          <Field
                            name="rapidProFlow"
                            label="RapidPro Flow"
                            style={{ width: '90%' }}
                            choices={
                              rapidProFlows
                                ? rapidProFlows.allRapidProFlows.map(
                                    (flow) => ({
                                      value: flow.id,
                                      name: flow.name,
                                    }),
                                  )
                                : []
                            }
                            component={FormikSelectField}
                          />
                        )}
                      </Box>
                    </Box>
                  </TabPanel>
                  <TabPanel value={selectedTab} index={1}>
                    <Box pt={3}>
                      <Field
                        name="confidenceInterval"
                        label={t('Confidence Interval')}
                        min={90}
                        max={99}
                        component={FormikSliderField}
                        suffix="%"
                      />
                      <Field
                        name="marginOfError"
                        label={t('Margin of Error')}
                        min={0}
                        max={9}
                        component={FormikSliderField}
                        suffix="%"
                      />
                      <Typography variant="caption">
                        {t('Cluster Filters')}
                      </Typography>
                      <Box flexDirection="column" display="flex">
                        <Box display="flex">
                          <Field
                            name="adminCheckbox"
                            label={t('Administrative Level')}
                            component={FormikCheckboxField}
                          />
                          <Field
                            name="ageCheckbox"
                            label={t(isSocialDctType ? 'Age' : 'Age of HoH')}
                            component={FormikCheckboxField}
                          />
                          <Field
                            name="sexCheckbox"
                            label={t(
                              isSocialDctType ? 'Gender' : 'Gender of HoH',
                            )}
                            component={FormikCheckboxField}
                          />
                        </Box>
                        {values.adminCheckbox && (
                          <Field
                            name="excludedAdminAreasRandom"
                            choices={mappedAdminAreas}
                            variant="outlined"
                            label={t('Filter Out Administrative Level Areas')}
                            component={FormikMultiSelectField}
                          />
                        )}

                        <Grid container>
                          {values.ageCheckbox && (
                            <Grid size={{ xs: 12 }}>
                              <Box mt={6}>
                                <Grid container>
                                  <Grid size={{ xs: 4 }}>
                                    <Field
                                      name="filterAgeMin"
                                      label={t('Minimum Age')}
                                      type="number"
                                      color="primary"
                                      component={FormikTextField}
                                    />
                                  </Grid>
                                  <Grid size={{ xs: 4 }}>
                                    <Field
                                      name="filterAgeMax"
                                      label={t('Maximum Age')}
                                      type="number"
                                      color="primary"
                                      component={FormikTextField}
                                    />
                                  </Grid>
                                </Grid>
                              </Box>
                            </Grid>
                          )}
                          {values.sexCheckbox && (
                            <Grid size={{ xs: 5 }}>
                              <Box mt={6}>
                                <Field
                                  name="filterSex"
                                  label={t('Gender')}
                                  color="primary"
                                  choices={[
                                    { value: 'FEMALE', name: t('Female') },
                                    { value: 'MALE', name: t('Male') },
                                    { value: 'OTHER', name: t('Other') },
                                    {
                                      value: 'NOT_COLLECTED',
                                      name: t('Not Collected'),
                                    },
                                    {
                                      value: 'NOT_ANSWERED',
                                      name: t('Not Answered'),
                                    },
                                  ]}
                                  component={FormikSelectField}
                                />
                              </Box>
                            </Grid>
                          )}
                        </Grid>
                      </Box>

                      <Box
                        pb={3}
                        pt={3}
                        fontSize={16}
                        fontWeight="fontWeightBold"
                      >
                        Sample size:{' '}
                        {isNaN(sampleSizesData?.sampleSize?.sampleSize)
                          ? ' 0'
                          : ` ${sampleSizesData?.sampleSize?.sampleSize}`}{' '}
                        out of{' '}
                        {isNaN(sampleSizesData?.sampleSize?.paymentRecordCount)
                          ? ' 0'
                          : ` ${sampleSizesData?.sampleSize?.paymentRecordCount}`}
                        {getSampleSizePercentage()}
                      </Box>
                      <Field
                        name="verificationChannel"
                        label="Verification Channel"
                        style={{
                          flexDirection: 'row',
                        }}
                        alignItems="center"
                        choices={[
                          {
                            value: 'RAPIDPRO',
                            name: 'RAPIDPRO',
                            dataCy: 'radio-rapidpro',
                          },
                          { value: 'XLSX', name: 'XLSX', dataCy: 'radio-xlsx' },
                          {
                            value: 'MANUAL',
                            name: 'MANUAL',
                            dataCy: 'radio-manual',
                          },
                        ]}
                        component={FormikRadioGroup}
                      />
                      {values.verificationChannel === 'RAPIDPRO' && (
                        <Field
                          name="rapidProFlow"
                          label="RapidPro Flow"
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
                    type="submit"
                    color="primary"
                    variant="contained"
                    onClick={submitForm}
                    data-cy="button-submit"
                  >
                    {t('SAVE')}
                  </LoadingButton>
                </DialogActions>
              </DialogFooter>
            </Dialog>
          </Form>
        );
      }}
    </Formik>
  );
};
