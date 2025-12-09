import { FieldAttribute } from '@restgenerated/models/FieldAttribute';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { UniversalCriteriaComponent } from './UniversalCriteriaComponent';
import { Button } from '@mui/material';

const PlainComponentWrapper = styled.div`
  display: flex;
  flex-direction: column;
  width: 100%;
`;
const ButtonWrapper = styled.div`
  display: flex;
  align-items: end;
  justify-content: end;
`;

interface UniversalCriteriaPlainComponentProps {
  rules?;
  arrayHelpers?;
  individualDataNeeded?: boolean;
  isEdit?: boolean;
  individualFieldsChoices: FieldAttribute[];
  householdFieldsChoices: FieldAttribute[];
}

export const UniversalCriteriaPlainComponent = (
  props: UniversalCriteriaPlainComponentProps,
): React.ReactElement => {
  const [isOpen, setOpen] = React.useState(false);
  const { t } = useTranslation();
  return (
    <PlainComponentWrapper>
      {props.isEdit && (
        <>
          {!!props.rules.length && (
            <ButtonWrapper>
              <Button
                variant="outlined"
                color="primary"
                onClick={() => setOpen(true)}
              >
                {t('Add')} &apos;Or&apos; {t('Filter')}
              </Button>
            </ButtonWrapper>
          )}
        </>
      )}
      <UniversalCriteriaComponent
        {...props}
        isAddDialogOpen={isOpen}
        onAddDialogClose={() => setOpen(false)}
      />
    </PlainComponentWrapper>
  );
};
