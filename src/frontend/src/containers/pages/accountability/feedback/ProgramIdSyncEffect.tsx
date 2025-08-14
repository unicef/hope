import React from 'react';
import { useFormikContext } from 'formik';

type FeedbackFormValues = {
  category: string;
  issueType: string | null;
  selectedHousehold: any;
  selectedIndividual: any;
  description: string;
  comments: string | null;
  admin2: any;
  area: string | null;
  language: string | null;
  consent: boolean;
  programId: string;
  verificationRequired: boolean;
};

export function ProgramIdSyncEffect() {
  const { values, setFieldValue } = useFormikContext<FeedbackFormValues>();
  React.useEffect(() => {
    if (
      values.selectedHousehold?.program?.id &&
      values.programId !== values.selectedHousehold.program.id
    ) {
      setFieldValue('programId', values.selectedHousehold.program.id);
    } else if (
      values.selectedIndividual?.program?.id &&
      values.programId !== values.selectedIndividual.program.id
    ) {
      setFieldValue('programId', values.selectedIndividual.program.id);
    }
  }, [
    values.selectedHousehold?.program?.id,
    values.selectedIndividual?.program?.id,
    values.programId,
    setFieldValue,
  ]);
  return null;
}
