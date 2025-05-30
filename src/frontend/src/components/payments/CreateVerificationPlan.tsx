import {
  Box,
  Button,
  DialogContent,
  DialogTitle,
  Grid2 as Grid,
  Typography,
} from '@mui/material';
import { Field, Form, Formik } from 'formik';
import { ChangeEvent, ReactElement, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';
import {
  useCreatePaymentVerificationPlanMutation,
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
import { getPercentage } from '@utils/utils';
import { AutoSubmitFormOnEnter } from '@core/AutoSubmitFormOnEnter';
import { ButtonTooltip } from '@core/ButtonTooltip';
import { FormikEffect } from '@core/FormikEffect';
import { LoadingButton } from '@core/LoadingButton';
import { TabPanel } from '@core/TabPanel';
import { Tabs, Tab } from '@core/Tabs';
import { RapidProFlowsLoader } from './RapidProFlowsLoader';
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
function prepareVariables(
  cashOrPaymentPlanId,
  selectedTab,
  values,
  businessArea,
) {
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
  canCreatePaymentVerificationPlan: boolean;
  version: number;
  isPaymentPlan: boolean;
}
export const CreateVerificationPlan = ({
  cashOrPaymentPlanId,
  canCreatePaymentVerificationPlan,
  version,
  isPaymentPlan,
}: Props): ReactElement => {
  const refetchQueries = usePaymentRefetchQueries(cashOrPaymentPlanId);
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const [selectedTab, setSelectedTab] = useState(0);
  const { showMessage } = useSnackbar();
  const [mutate, { loading }] = useCreatePaymentVerificationPlanMutation();
  const { businessArea, baseUrl, programId: programSlug } = useBaseUrl();
  const { isActiveProgram, isSocialDctType } = useProgramContext();
  const [formValues, setFormValues] = useState(initialValues);

  const { data: rapidProFlowsData, refetch: refetchRapidProFlows } = useQuery({
    queryKey: ['rapidProFlows', businessArea, programSlug],
    queryFn: () =>
      RestService.restBusinessAreasProgramsSurveysAvailableFlowsList({
        businessAreaSlug: businessArea,
        programSlug: programSlug,
      }),
    enabled: false,
  });

  const rapidProFlows = rapidProFlowsData
    ? { allRapidProFlows: rapidProFlowsData.results }
    : null;
  const loadRapidProFlows = refetchRapidProFlows;

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
      selectedTab,
      formValues,
      businessArea,
    ),
    fetchPolicy: 'network-only',
  });

  useEffect(() => {
    if (open) {
      loadSampleSize();
    }
  }, [formValues, open, loadSampleSize]);

  const submit = async (values): Promise<void> => {
    try {
      const { errors } = await mutate({
        variables: {
          ...prepareVariables(
            cashOrPaymentPlanId,
            selectedTab,
            values,
            businessArea,
          ),
          version,
        },
        refetchQueries,
      });
      setOpen(false);

      if (errors) {
        showMessage(t('Error while submitting'));
        return;
      }
      showMessage(t('New verification plan created.'));
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  const mappedAdminAreas = adminAreasData?.results?.length
    ? adminAreasData.results.map((area) => ({
        value: area.id,
        name: area.name || '',
      }))
    : [];

  const handleFormChange = (values): void => {
    setFormValues(values);
  };

  const getSampleSizePercentage = (): string => {
    const sampleSize = sampleSizesData?.sampleSize?.sampleSize;
    const paymentRecordCount = sampleSizesData?.sampleSize?.paymentRecordCount;

    if (isNaN(sampleSize) || isNaN(paymentRecordCount)) {
      return '';
    }

    return `(${getPercentage(sampleSize, paymentRecordCount)})`;
  };

  const getTooltipTitle = (): string => {
    if (!canCreatePaymentVerificationPlan) {
      return t(
        'There are no payment records that could be assigned to a new Verification Plan.',
      );
    }
    if (!isActiveProgram) {
      return t('Program has to be active to create a Verification Plan');
    }
    return '';
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
              lastSuccessfulPage: `/${baseUrl}/payment-verification/${isPaymentPlan ? 'payment-plan' : 'cash-plan'}/${cashOrPaymentPlanId}`,
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
            <Box mr={2}>
              <ButtonTooltip
                title={getTooltipTitle()}
                disabled={!isActiveProgram || !canCreatePaymentVerificationPlan}
                color="primary"
                variant="contained"
                onClick={() => setOpen(true)}
                data-cy="button-new-plan"
              >
                {t('CREATE VERIFICATION PLAN')}
              </ButtonTooltip>
            </Box>
            <Dialog
              open={open}
              onClose={() => setOpen(false)}
              scroll="paper"
              aria-labelledby="form-dialog-title"
              maxWidth="md"
            >
              <DialogTitleWrapper>
                <DialogTitle data-cy="dialog-title">
                  {t('Create Verification Plan')}
                </DialogTitle>
              </DialogTitleWrapper>
              <DialogContent>
                <DialogContainer>
                  <TabsContainer>
                    <StyledTabs
                      data-cy="tabs"
                      value={selectedTab}
                      onChange={(
                        event: ChangeEvent<unknown>,
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
                        <Box pt={3}>
                          <Box
                            pb={3}
                            pt={3}
                            fontSize={16}
                            fontWeight="fontWeightBold"
                          >
                            Sample size:{' '}
                            {isNaN(sampleSizesData?.sampleSize?.sampleSize)
                              ? ''
                              : sampleSizesData?.sampleSize?.sampleSize}{' '}
                            out of{' '}
                            {isNaN(
                              sampleSizesData?.sampleSize?.paymentRecordCount,
                            )
                              ? ''
                              : sampleSizesData?.sampleSize?.paymentRecordCount}
                            {getSampleSizePercentage()}
                          </Box>
                        </Box>
                        <Box fontSize={12} color="#797979">
                          {t('This option is recommended for RapidPro')}
                        </Box>
                        <Field
                          name="verificationChannel"
                          label={t('Verification Channel')}
                          style={{ flexDirection: 'row' }}
                          data-cy="checkbox-verification-channel"
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
                            label={t('RapidPro Flow')}
                            style={{ width: '90%' }}
                            choices={
                              rapidProFlows?.allRapidProFlows?.map((flow) => ({
                                value: flow.uuid,
                                name: flow.name,
                              })) || []
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
                        dataCy="slider-confidence-interval"
                      />
                      <Field
                        name="marginOfError"
                        label={t('Margin of Error')}
                        min={0}
                        max={9}
                        component={FormikSliderField}
                        suffix="%"
                        dataCy="slider-margin-of-error"
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
                        Sample size: {sampleSizesData?.sampleSize?.sampleSize}{' '}
                        out of {sampleSizesData?.sampleSize?.paymentRecordCount}
                        {getSampleSizePercentage()}
                      </Box>
                      <Field
                        name="verificationChannel"
                        label={t('Verification Channel')}
                        style={{ flexDirection: 'row' }}
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
                            rapidProFlows
                              ? rapidProFlows.allRapidProFlows.map((flow) => ({
                                  value: flow.uuid,
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
                  <Button
                    data-cy="button-cancel"
                    onClick={() => setOpen(false)}
                  >
                    CANCEL
                  </Button>
                  <LoadingButton
                    loading={loading}
                    type="submit"
                    color="primary"
                    variant="contained"
                    onClick={submitForm}
                    data-cy="button-submit"
                  >
                    SAVE
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
