import { useTranslation } from 'react-i18next';
import { Field } from 'formik';
import { useBusinessAreaDataQuery, useProgramQuery } from '@generated/graphql';
import { FormikCheckboxField } from '@shared/Formik/FormikCheckboxField';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { ReactElement } from 'react';

export function ScreenBeneficiaryField(): ReactElement {
  const { t } = useTranslation();
  const { programId } = useBaseUrl();
  const { data: programData } = useProgramQuery({
    variables: { id: programId },
  });
  if (!programData?.program?.screenBeneficiary) {
    return null;
  }
  return (
    <Field
      name="screenBeneficiary"
      label={t('Screen Beneficiary')}
      color="primary"
      component={FormikCheckboxField}
    />
  );
}
