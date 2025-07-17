import { useTranslation } from 'react-i18next';
import { Field } from 'formik';
import { useProgramQuery } from '@generated/graphql';
import { FormikCheckboxField } from '@shared/Formik/FormikCheckboxField';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { ReactElement } from 'react';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { ProgramDetail } from '@restgenerated/models/ProgramDetail';

export function ScreenBeneficiaryField(): ReactElement {
  const { t } = useTranslation();
  const { programId } = useBaseUrl();
  const { data: programData } = useProgramQuery({
    variables: { id: programId },
  const { programSlug, businessAreaSlug } = useBaseUrl();
  const { data: program, isLoading } = useQuery<ProgramDetail>({
    queryKey: ['program', businessAreaSlug, programSlug],
    queryFn: () =>
      RestService.restBusinessAreasProgramsRetrieve({
        businessAreaSlug: businessAreaSlug,
        slug: programSlug,
      }),
  });
  if (!programData?.program?.screenBeneficiary) {
  if (isLoading) {
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
