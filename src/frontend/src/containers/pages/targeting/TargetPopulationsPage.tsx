import { AutoSubmitFormOnEnter } from '@components/core/AutoSubmitFormOnEnter';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import withErrorBoundary from '@components/core/withErrorBoundary';
import * as Yup from 'yup';
import { CreateTPMenu } from '@components/targeting/CreateTPMenu';
import ProgramEligibilityCriteriaDisplay from '@components/targeting/ProgramEligibilityCriteriaDisplay';
import { TargetPopulationForPeopleFilters } from '@components/targeting/TargetPopulationForPeopleFilters';
import { TargetPopulationTableFilters } from '@components/targeting/TargetPopulationTableFilters';
import { TargetPopulationForPeopleTable } from '@containers/tables/targeting/TargetPopulationForPeopleTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useScrollToRefOnChange } from '@hooks/useScrollToRefOnChange';
import { Info } from '@mui/icons-material';
import { Box, Button, IconButton, Paper, Typography } from '@mui/material';
import { getFilterFromQueryParams } from '@utils/utils';
import { FieldArray, Form, Formik } from 'formik';
import { ReactElement, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import { useProgramContext } from 'src/programContext';
import { PERMISSIONS, hasPermissions } from '../../../config/permissions';
import { TargetingInfoDialog } from '../../dialogs/targetPopulation/TargetingInfoDialog';
import { TargetPopulationTable } from '../../tables/targeting/TargetPopulationTable';

const initialFilter = {
  name: '',
  status: '',
  totalHouseholdsCountGte: '',
  totalHouseholdsCountLte: '',
  createdAtGte: '',
  createdAtLte: '',
};

const TargetPopulationsPage = (): ReactElement => {
  const location = useLocation();
  const { t } = useTranslation();
  const permissions = usePermissions();
  const { programSlug } = useBaseUrl();
  const { isSocialDctType, isStandardDctType, screenBeneficiary } =
    useProgramContext();

  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [shouldScroll, setShouldScroll] = useState(false);
  const tableRef = useRef<HTMLDivElement>(null);
  useScrollToRefOnChange(tableRef, shouldScroll, appliedFilter, () =>
    setShouldScroll(false),
  );
  const [isInfoOpen, setToggleInfo] = useState(false);

  const canCreate = hasPermissions(PERMISSIONS.TARGETING_CREATE, permissions);

  const initialValues = {
    criterias: [],
    program: programSlug,
    programCycleId: {
      value: '',
      name: '',
    },
    excludedIds: '',
    exclusionReason: '',
    flagExcludeIfActiveAdjudicationTicket: false,
    flagExcludeIfOnSanctionList: false,
    householdIds: '',
    individualIds: '',
    deliveryMechanism: '',
    fsp: '',
  };

  const validationSchema = Yup.object()
    .shape({
      criterias: Yup.array(),
      householdIds: Yup.string(),
      individualIds: Yup.string(),
    })
    .test(
      'at-least-one-filled',
      'At least one of Programme Eligibility Criteria, Household IDs, or Individual IDs must be filled.',
      function (values) {
        const hasCriterias =
          Array.isArray(values.criterias) && values.criterias.length > 0;
        const hasHouseholdIds =
          typeof values.householdIds === 'string' &&
          values.householdIds.trim() !== '';
        const hasIndividualIds =
          typeof values.individualIds === 'string' &&
          values.individualIds.trim() !== '';
        return hasCriterias || hasHouseholdIds || hasIndividualIds;
      },
    );

  if (!permissions) return null;
  if (!hasPermissions(PERMISSIONS.TARGETING_VIEW_LIST, permissions))
    return <PermissionDenied />;
  let Table = TargetPopulationTable;
  let Filters = TargetPopulationTableFilters;
  if (isSocialDctType) {
    Table = TargetPopulationForPeopleTable;
    Filters = TargetPopulationForPeopleFilters;
  }

  return (
    <>
      <PageHeader title={t('Targeting')}>
        <>
          <IconButton
            onClick={() => setToggleInfo(true)}
            color="primary"
            aria-label="Targeting Information"
            data-cy="button-target-population-info"
          >
            <Info />
          </IconButton>
          <TargetingInfoDialog open={isInfoOpen} setOpen={setToggleInfo} />
          {canCreate && <CreateTPMenu />}
        </>
      </PageHeader>
      <Filters
        filter={filter}
        setFilter={setFilter}
        initialFilter={initialFilter}
        appliedFilter={appliedFilter}
        setAppliedFilter={(newFilter) => {
          setAppliedFilter(newFilter);
          setShouldScroll(true);
        }}
      />
      <Box p={6}>
        <Paper>
          <Formik
            initialValues={initialValues}
            validationSchema={validationSchema}
            onSubmit={(values) => console.log('Submitting form', values)}
          >
            {({ submitForm, values, errors, isValid }) => {
              console.log('values', values);
              console.log('errors', errors);
              console.log('isValid', isValid);
              return (
                <Form>
                  <AutoSubmitFormOnEnter />
                  <Box
                    display="flex"
                    alignItems="center"
                    justifyContent="space-between"
                    p={2}
                  >
                    <Typography variant="h6" p={0}>
                      {t('Programme Eligibility Criteria')}
                    </Typography>
                    <Button
                      variant="contained"
                      color="primary"
                      onClick={() => {
                        console.log('Save button clicked');
                        console.log('Form is valid:', isValid);
                        console.log('Form errors:', errors);
                        submitForm();
                      }}
                      sx={{ mr: 2 }}
                    >
                      {t('Save')}
                    </Button>
                  </Box>
                  <Box p={3}>
                    <FieldArray
                      name="criterias"
                      render={(arrayHelpers) => (
                        <ProgramEligibilityCriteriaDisplay
                          helpers={arrayHelpers}
                          rules={values.criterias}
                          screenBeneficiary={screenBeneficiary}
                          isStandardDctType={isStandardDctType}
                          isSocialDctType={isSocialDctType}
                          isEdit
                        />
                      )}
                    />
                  </Box>
                </Form>
              );
            }}
          </Formik>
        </Paper>
      </Box>

      <Box ref={tableRef}>
        <Table
          filter={appliedFilter}
          canViewDetails={hasPermissions(
            PERMISSIONS.TARGETING_VIEW_DETAILS,
            permissions,
          )}
        />
      </Box>
    </>
  );
};

export default withErrorBoundary(
  TargetPopulationsPage,
  'TargetPopulationsPage',
);
