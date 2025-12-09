import { FieldAttribute } from '@restgenerated/models/FieldAttribute';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { UniversalCriteriaComponent } from './UniversalCriteriaComponent';
import { Button, Grid } from '@mui/material';

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
        <Grid container spacing={2}>
          <Grid size={{ xs: 6 }}>
            {!!props.rules.length && (
              <ButtonWrapper>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={() => setOpen(true)}
                >
                  {t('Add')} &apos;Or&apos; {t('Filter')}
                </Button>
              </ButtonWrapper>
            )}
          </Grid>
        </Grid>
      )}
      <UniversalCriteriaComponent
        {...props}
        isAddDialogOpen={isOpen}
        onAddDialogClose={() => setOpen(false)}
      />
    </PlainComponentWrapper>
  );
};
