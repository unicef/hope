import { Grid2 as Grid } from '@mui/material';
import { Field } from 'formik';
import { useTranslation } from 'react-i18next';
import { GrievancesChoiceDataQuery } from '@generated/graphql';
import { useArrayToDict } from '@hooks/useArrayToDict';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { DividerLine } from '@core/DividerLine';
import { LabelizedField } from '@core/LabelizedField';
import { useProgramContext } from 'src/programContext';
import {
  getGrievanceCategoryDescriptions,
  getGrievanceIssueTypeDescriptions,
  GRIEVANCE_CATEGORIES_NAMES,
  GRIEVANCE_ISSUE_TYPES_NAMES,
} from '@utils/constants';
import { ChangeEvent, ReactElement } from 'react';
import withErrorBoundary from '@components/core/withErrorBoundary';

export interface SelectionProps {
  handleChange: (e: ChangeEvent) => void;
  choicesData: GrievancesChoiceDataQuery;
  setFieldValue: (field: string, value, shouldValidate?: boolean) => void;
  showIssueType: (values) => boolean;
  values;
  redirectedFromRelatedTicket: boolean;
}

function Selection({
  handleChange,
  choicesData,
  setFieldValue,
  showIssueType,
  values,
  redirectedFromRelatedTicket,
}: SelectionProps): ReactElement {
  const { t } = useTranslation();
  const { isSocialDctType } = useProgramContext();
  const issueTypeDict = useArrayToDict(
    choicesData?.grievanceTicketIssueTypeChoices,
    'category',
    '*',
  );

  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const dataChangeIssueTypes = [
    { name: `${beneficiaryGroup?.groupLabel} Data Update`, value: '13' },
    { name: `${beneficiaryGroup?.memberLabel} Data Update`, value: '14' },
  ];

  function replaceLabels(choices, _beneficiaryGroup) {
    if (!choices) return [];
    return choices.map((choice) => {
      let newName = choice.name;
      if (_beneficiaryGroup?.memberLabel) {
        newName = newName.replace(/Individual/g, _beneficiaryGroup.memberLabel);
      }
      if (_beneficiaryGroup?.groupLabel) {
        newName = newName.replace(/Household/g, _beneficiaryGroup.groupLabel);
      }
      return { ...choice, name: newName };
    });
  }
  const updatedChoices = replaceLabels(
    issueTypeDict[values.category]?.subCategories,
    beneficiaryGroup,
  );

  const categoryDescriptions =
    getGrievanceCategoryDescriptions(beneficiaryGroup);
  const issueTypeDescriptions =
    getGrievanceIssueTypeDescriptions(beneficiaryGroup);

  const issueTypeChoices = redirectedFromRelatedTicket
    ? dataChangeIssueTypes
    : updatedChoices;

  const addDisabledProperty = (choices) => {
    if (!choices) return [];
    if (!isSocialDctType) return choices;

    return choices.map((choice) => {
      if (
        //Add individual
        choice.value === '16' ||
        //HH data update
        choice.value === '13' ||
        //Withdraw HH
        choice.value === '17'
      ) {
        return { ...choice, disabled: true };
      }
      return choice;
    });
  };
  const issueTypeChoicesBasedOnDctType = addDisabledProperty(
    redirectedFromRelatedTicket ? dataChangeIssueTypes : issueTypeChoices,
  );

  const categoryDescription =
    categoryDescriptions[GRIEVANCE_CATEGORIES_NAMES[values.category]] || '';
  const issueTypeDescription =
    issueTypeDescriptions[GRIEVANCE_ISSUE_TYPES_NAMES[values.issueType]] || '';

  return (
    <Grid container spacing={3}>
      <Grid size={{ xs: 6 }}>
        <Field
          name="category"
          label="Category"
          onChange={(e) => {
            setFieldValue('issueType', null);
            handleChange(e);
          }}
          variant="outlined"
          choices={choicesData.grievanceTicketManualCategoryChoices}
          component={FormikSelectField}
          disabled={redirectedFromRelatedTicket}
          required
        />
      </Grid>
      {showIssueType(values) && (
        <Grid size={{ xs: 6 }}>
          <Field
            name="issueType"
            label="Issue Type"
            variant="outlined"
            choices={issueTypeChoicesBasedOnDctType}
            component={FormikSelectField}
            required
          />
        </Grid>
      )}
      {values.category && (
        <>
          <DividerLine />
          <Grid size={{ xs: 6 }}>
            <LabelizedField label={t('Category Description')}>
              {categoryDescription}
            </LabelizedField>
          </Grid>
          {issueTypeDescription && (
            <Grid size={{ xs: 6 }}>
              <LabelizedField label={t('Issue Type Description')}>
                {issueTypeDescription}
              </LabelizedField>
            </Grid>
          )}
        </>
      )}
    </Grid>
  );
}

export default withErrorBoundary(Selection, 'Selection');
