import withErrorBoundary from '@components/core/withErrorBoundary';
import { useBaseUrl } from '@hooks/useBaseUrl';
import CalendarTodayRoundedIcon from '@mui/icons-material/CalendarTodayRounded';
import { Tooltip } from '@mui/material';
import type { PaginatedBeneficiaryGroupList } from '@restgenerated/models/PaginatedBeneficiaryGroupList';
import type { ProgramChoices } from '@restgenerated/models/ProgramChoices';
import { RestService } from '@restgenerated/services/RestService';
import { FormikCheckboxField } from '@shared/Formik/FormikCheckboxField';
import { FormikDateField } from '@shared/Formik/FormikDateField';
import { PaymentPlanPurposesAutocomplete } from '@shared/autocompletes/rest/PaymentPlanPurposesAutocomplete';
import { FormikRadioGroup } from '@shared/Formik/FormikRadioGroup';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { useQuery } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import { Field, Form, useFormikContext } from 'formik';
import type { ReactElement } from 'react';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import {
  ResponsiveGrid,
  ResponsiveGridContainer,
  responsiveValue,
} from 'src/responsive';

interface ProgramFormPropTypes {
  values;
  programHasRdi?: boolean;
  errors;
  lockedPurposeIds?: string[];
}

const ProgramForm = ({
  values,
  programHasRdi,
  lockedPurposeIds,
}: ProgramFormPropTypes): ReactElement => {
  const { t } = useTranslation();
  const location = useLocation();
  const { businessArea } = useBaseUrl();
  const isEditProgram = location.pathname.indexOf('edit') !== -1;

  const { data } = useQuery<ProgramChoices>({
    queryKey: restQueryKey(RestService.restChoicesProgramsRetrieve),
    queryFn: () => RestService.restChoicesProgramsRetrieve(),
    staleTime: 1000 * 60 * 10,
    gcTime: 1000 * 60 * 30,
  });

  const { data: dataCollectingTypeChoices } = useQuery({
    queryKey: restQueryKey(
      RestService.restBusinessAreasDataCollectingTypesChoicesList,
      { businessAreaSlug: businessArea },
    ),
    queryFn: () =>
      RestService.restBusinessAreasDataCollectingTypesChoicesList({
        businessAreaSlug: businessArea,
      }),
    staleTime: 1000 * 60 * 10,
    gcTime: 1000 * 60 * 30,
  });

  const { data: beneficiaryGroupsData } =
    useQuery<PaginatedBeneficiaryGroupList>({
      queryKey: restQueryKey(RestService.restBeneficiaryGroupsList),
      queryFn: () => RestService.restBeneficiaryGroupsList({}),
    });

  const { setFieldValue } = useFormikContext();

  const isCopyProgramPage = location.pathname.includes('duplicate');

  // For copy program pages, filter DCTs based on Beneficiary Group (BG → DCT)
  // For normal create/edit, filter BGs based on DCT (DCT → BG)
  const filteredDataCollectionTypeChoicesData = useMemo(() => {
    const allDCTs = dataCollectingTypeChoices?.filter((el) => el.name !== '');

    if (
      !isCopyProgramPage ||
      !values.beneficiaryGroup ||
      !beneficiaryGroupsData?.results
    ) {
      return allDCTs;
    }

    // Find the selected beneficiary group to determine its masterDetail property
    const selectedBG = beneficiaryGroupsData.results.find(
      (bg) => String(bg.id) === String(values.beneficiaryGroup),
    );

    if (!selectedBG) return allDCTs;

    // Filter DCTs based on beneficiary group's masterDetail property
    return allDCTs?.filter((dct) => {
      if (selectedBG.masterDetail === true) {
        return dct.type === 'STANDARD';
      } else if (selectedBG.masterDetail === false) {
        return dct.type === 'SOCIAL';
      }
      return true;
    });
  }, [
    dataCollectingTypeChoices,
    isCopyProgramPage,
    values.beneficiaryGroup,
    beneficiaryGroupsData,
  ]);

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

    if (!beneficiaryGroupsData?.results) return [];

    // For copy program pages, show all beneficiary groups (no filtering)
    if (isCopyProgramPage) {
      return beneficiaryGroupsData.results.map((el) => ({
        name: el.name,
        value: el.id,
      }));
    }

    // For normal create/edit, filter BGs based on DCT
    const dctType = getTypeByDataCollectingTypeCode(
      values.dataCollectingTypeCode,
    );

    let filteredBeneficiaryGroups;

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
    isCopyProgramPage,
  ]);

  if (!data || !beneficiaryGroupsData || !dataCollectingTypeChoices)
    return null;

  return (
    <Form>
      <ResponsiveGridContainer spacing={3}>
        <ResponsiveGrid size="half">
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
        </ResponsiveGrid>
        <ResponsiveGrid size="half">
          <Field
            name="code"
            label={t('Programme Code')}
            type="text"
            fullWidth
            variant="outlined"
            component={FormikTextField}
            maxLength={4}
            disabled={isEditProgram}
            data-cy="input-programme-code"
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="half">
          <Field
            name="startDate"
            label={t('Start Date')}
            component={FormikDateField}
            required
            fullWidth
            decoratorEnd={<CalendarTodayRoundedIcon color="disabled" />}
            data-cy="input-start-date"
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="half">
          <Field
            name="endDate"
            label={t('End Date')}
            component={FormikDateField}
            disabled={!values.startDate}
            initialFocusedDate={values.startDate}
            fullWidth
            decoratorEnd={<CalendarTodayRoundedIcon color="disabled" />}
            minDate={values.startDate}
            data-cy="input-end-date"
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="half">
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
        </ResponsiveGrid>
        <ResponsiveGrid size="half">
          <Tooltip
            title={
              values.isActive
                ? 'Cannot update Data Collecting Type when program is Active'
                : programHasRdi
                  ? 'Field disabled because Programme has RDI'
                  : isCopyProgramPage
                    ? 'Field disabled on Copy Programme page'
                    : ''
            }
            placement="top"
          >
            <span>
              <Field
                name="dataCollectingTypeCode"
                label={t('Data Collecting Type')}
                fullWidth
                variant="outlined"
                required
                disabled={programHasRdi || isCopyProgramPage || values.isActive}
                onChange={(e) => {
                  // Only clear Beneficiary Group if NOT copying a program
                  if (!isCopyProgramPage) {
                    setFieldValue('beneficiaryGroup', '');
                  }
                  setFieldValue('dataCollectingTypeCode', e.target.value);
                }}
                choices={filteredDataCollectionTypeChoicesData || []}
                component={FormikSelectField}
                data-cy="input-data-collecting-type"
              />
            </span>
          </Tooltip>
        </ResponsiveGrid>
        <ResponsiveGrid size="half">
          <Tooltip
            title={
              isCopyProgramPage
                ? 'Beneficiary Group is fixed when copying programs'
                : !values.dataCollectingTypeCode
                  ? 'Select Data Collecting Type first'
                  : programHasRdi
                    ? 'Field disabled because program has RDI'
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
                  (isCopyProgramPage && !!values.beneficiaryGroup) ||
                  (!values.dataCollectingTypeCode && !isCopyProgramPage) ||
                  programHasRdi
                }
              />
            </span>
          </Tooltip>
        </ResponsiveGrid>
        <ResponsiveGrid size="full">
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
        </ResponsiveGrid>
        <ResponsiveGrid size="full">
          <Field
            name="paymentPlanPurposes"
            required
            component={PaymentPlanPurposesAutocomplete}
            lockedValues={lockedPurposeIds ?? []}
            disabled={(values.paymentPlanPurposes?.length ?? 0) >= 10}
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="half">
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
        </ResponsiveGrid>
        <ResponsiveGrid size="half">
          <Field
            name="administrativeAreasOfImplementation"
            label={t('Administrative Areas of Implementation')}
            type="text"
            fullWidth
            variant="outlined"
            component={FormikTextField}
            data-cy="input-admin-area"
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="half">
          <Field
            name="populationGoal"
            label={t('Population Goal (# of Individuals)')}
            type="number"
            fullWidth
            variant="outlined"
            component={FormikTextField}
            data-cy="input-population-goal"
          />
        </ResponsiveGrid>
        <ResponsiveGrid
          size="half"
          sx={{ display: responsiveValue('none', 'block') }}
        />
        <ResponsiveGrid size="half">
          <Field
            name="cashPlus"
            label={t('Cash+')}
            color="primary"
            component={FormikCheckboxField}
            data-cy="input-cash-plus"
          />
        </ResponsiveGrid>
        <ResponsiveGrid
          size="half"
          sx={{ display: responsiveValue('none', 'block') }}
        />
        <ResponsiveGrid size="full">
          <Field
            name="frequencyOfPayments"
            label={t('Frequency of Payment')}
            choices={data.frequencyOfPaymentsChoices}
            component={FormikRadioGroup}
            data-cy="input-frequency-of-payment"
            alignItems="center"
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="half">
          <Field
            name="reconciliationWindowInDays"
            label={t('Reconciliation window (in days)')}
            type="number"
            fullWidth
            integer
            variant="outlined"
            component={FormikTextField}
            data-cy="input-reconciliation-window"
          />
        </ResponsiveGrid>
        <ResponsiveGrid size="half">
          <Field
            name="sendReconciliationWindowExpiryNotifications"
            label={t('Send reconciliation window expiry notifications')}
            color="primary"
            component={FormikCheckboxField}
            data-cy="input-reconciliation-window-notifications"
          />
        </ResponsiveGrid>
      </ResponsiveGridContainer>
    </Form>
  );
};

export default withErrorBoundary(ProgramForm, 'ProgramForm');
