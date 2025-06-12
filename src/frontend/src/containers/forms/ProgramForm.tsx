import withErrorBoundary from '@components/core/withErrorBoundary';
import { useBaseUrl } from '@hooks/useBaseUrl';
import CalendarTodayRoundedIcon from '@mui/icons-material/CalendarTodayRounded';
import { Grid2 as Grid, Tooltip } from '@mui/material';
import { PaginatedBeneficiaryGroupList } from '@restgenerated/models/PaginatedBeneficiaryGroupList';
import { ProgramChoices } from '@restgenerated/models/ProgramChoices';
import { RestService } from '@restgenerated/services/RestService';
import { FormikCheckboxField } from '@shared/Formik/FormikCheckboxField';
import { FormikDateField } from '@shared/Formik/FormikDateField';
import { FormikRadioGroup } from '@shared/Formik/FormikRadioGroup';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { useQuery } from '@tanstack/react-query';
import { Field, Form, useFormikContext } from 'formik';
import { ReactElement, useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';

interface ProgramFormPropTypes {
  values;
  programHasRdi?: boolean;
}

const ProgramForm = ({
  values,
  programHasRdi,
}: ProgramFormPropTypes): ReactElement => {
  const { t } = useTranslation();
  const location = useLocation();
  const { businessArea } = useBaseUrl();
  const isEditProgram = location.pathname.includes('edit');

  const { data } = useQuery<ProgramChoices>({
    queryKey: ['programChoices', businessArea],
    queryFn: () =>
      RestService.restBusinessAreasProgramsChoicesRetrieve({
        businessAreaSlug: businessArea,
      }),
  });

  const { data: beneficiaryGroupsData } =
    useQuery<PaginatedBeneficiaryGroupList>({
      queryKey: ['beneficiaryGroups'],
      queryFn: () => RestService.restBeneficiaryGroupsList({}),
    });

  const { setFieldValue } = useFormikContext();

  const stableSetFieldValue = useCallback(
    (field: string, value: any, shouldValidate?: boolean) => {
      setFieldValue(field, value, shouldValidate);
    },
    [setFieldValue],
  );

  const filteredDataCollectionTypeChoicesData =
    data?.dataCollectingTypeChoices.filter((el) => el.name !== '');

  const mappedBeneficiaryGroupsData = useMemo(() => {
    function getTypeByDataCollectingTypeCode(
      dataCollectingTypeCode: string,
    ): string | undefined {
      if (!filteredDataCollectionTypeChoicesData) return undefined;
      const foundObject = filteredDataCollectionTypeChoicesData.find(
        (item) => item.value === dataCollectingTypeCode,
      );
      return foundObject ? foundObject.type : undefined;
    }
    const dctType = getTypeByDataCollectingTypeCode(
      values.dataCollectingTypeCode,
    );

    if (!beneficiaryGroupsData?.results) return [];

    let filteredBeneficiaryGroups = [];

    if (dctType === 'SOCIAL') {
      filteredBeneficiaryGroups = beneficiaryGroupsData.results.filter(
        (el) => el.masterDetail === false,
      );
    } else if (dctType === 'STANDARD') {
      filteredBeneficiaryGroups = beneficiaryGroupsData.results.filter(
        (el) => el.masterDetail === true,
      );
    } else {
      filteredBeneficiaryGroups = beneficiaryGroupsData.results;
    }

    return filteredBeneficiaryGroups.map((el) => ({
      name: el.name,
      value: el.id,
    }));
  }, [
    values.dataCollectingTypeCode,
    beneficiaryGroupsData,
    filteredDataCollectionTypeChoicesData,
  ]);

  const isCopyProgramPage = location.pathname.includes('duplicate');

  if (!data || !beneficiaryGroupsData) return null;

  return (
    <Form>
      <Grid container spacing={3}>
        <Grid size={{ xs: 6 }}>
          <Field
            name="name"
            label={t('Programme Name')}
            type="text"
            fullWidth
            required
            variant="outlined"
            component={FormikTextField}
            data-cy="input-programme-name"
          />
        </Grid>
        <Grid size={{ xs: 6 }}>
          <Field
            name="programmeCode"
            label={t('Programme Code')}
            type="text"
            fullWidth
            variant="outlined"
            component={FormikTextField}
            maxLength={4}
            data-cy="input-programme-code"
            disabled={isEditProgram}
          />
        </Grid>
        <Grid size={{ xs: 6 }}>
          <Field
            name="startDate"
            label={t('Start Date')}
            component={FormikDateField}
            required
            fullWidth
            decoratorEnd={<CalendarTodayRoundedIcon color="disabled" />}
            data-cy="input-start-date"
          />
        </Grid>
        <Grid size={{ xs: 6 }}>
          <Field
            name="endDate"
            label={t('End Date')}
            component={FormikDateField}
            disabled={!values.startDate}
            initialFocusedDate={values.startDate}
            fullWidth
            required={values.editMode}
            decoratorEnd={<CalendarTodayRoundedIcon color="disabled" />}
            minDate={values.startDate}
            data-cy="input-end-date"
          />
        </Grid>
        <Grid size={{ xs: 6 }}>
          <Field
            name="sector"
            label={t('Sector')}
            fullWidth
            required
            variant="outlined"
            choices={data.sectorChoices}
            component={FormikSelectField}
            data-cy="input-sector"
          />
        </Grid>
        <Grid size={{ xs: 6 }}>
          <Field
            name="dataCollectingTypeCode"
            label={t('Data Collecting Type')}
            fullWidth
            variant="outlined"
            required
            onChange={(e) => {
              setFieldValue('beneficiaryGroup', '');
              setFieldValue('dataCollectingTypeCode', e.target.value);
            }}
            choices={filteredDataCollectionTypeChoicesData || []}
            component={FormikSelectField}
            data-cy="input-data-collecting-type"
          />
        </Grid>
        <Grid size={{ xs: 6 }}>
          <Tooltip
            title={
              !values.dataCollectingTypeCode
                ? 'Select Data Collecting Type first'
                : programHasRdi
                  ? 'Field disabled because program has RDI'
                  : isCopyProgramPage
                    ? 'Field disabled for duplicate programs'
                    : ''
            }
            placement="top"
          >
            <span>
              <Field
                name="beneficiaryGroup"
                label={t('Beneficiary Group')}
                fullWidth
                variant="outlined"
                required={
                  !!values.dataCollectingTypeCode &&
                  !programHasRdi &&
                  !isCopyProgramPage
                }
                choices={mappedBeneficiaryGroupsData}
                component={FormikSelectField}
                data-cy="input-beneficiary-group"
                disabled={
                  !values.dataCollectingTypeCode ||
                  programHasRdi ||
                  isCopyProgramPage
                }
              />
            </span>
          </Tooltip>
        </Grid>
        <Grid size={{ xs: 12 }}>
          <Field
            name="description"
            label={t('Description')}
            type="text"
            fullWidth
            multiline
            variant="outlined"
            component={FormikTextField}
            data-cy="input-description"
          />
        </Grid>
        <Grid size={{ xs: 6 }}>
          <Field
            name="budget"
            label={t('Budget (USD)')}
            type="number"
            fullWidth
            precision={2}
            variant="outlined"
            component={FormikTextField}
            data-cy="input-budget"
          />
        </Grid>
        <Grid size={{ xs: 6 }}>
          <Field
            name="administrativeAreasOfImplementation"
            label={t('Administrative Areas of Implementation')}
            type="text"
            fullWidth
            variant="outlined"
            component={FormikTextField}
            data-cy="input-admin-area"
          />
        </Grid>
        <Grid size={{ xs: 6 }}>
          <Field
            name="populationGoal"
            label={t('Population Goal (# of Individuals)')}
            type="number"
            fullWidth
            variant="outlined"
            component={FormikTextField}
            data-cy="input-population-goal"
          />
        </Grid>
        <Grid size={{ xs: 6 }} />
        <Grid size={{ xs: 6 }}>
          <Field
            name="cashPlus"
            label={t('Cash+')}
            color="primary"
            component={FormikCheckboxField}
            data-cy="input-cash-plus"
          />
        </Grid>
        <Grid size={{ xs: 6 }} />
        <Grid size={{ xs: 6 }}>
          <Field
            name="frequencyOfPayments"
            label={t('Frequency of Payment')}
            choices={data.frequencyOfPaymentsChoices}
            component={FormikRadioGroup}
            data-cy="input-frequency-of-payment"
            alignItems="center"
          />
        </Grid>
      </Grid>
    </Form>
  );
};

export default withErrorBoundary(ProgramForm, 'ProgramForm');
