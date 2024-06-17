import { Box, Button } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { FieldAttributeNode } from '../../../__generated__/graphql';
import { UniversalCriteriaComponent } from './UniversalCriteriaComponent';

interface UniversalCriteriaPlainComponentProps {
  rules?;
  arrayHelpers?;
  individualDataNeeded?: boolean;
  isEdit?: boolean;
  individualFieldsChoices: FieldAttributeNode[];
  householdFieldsChoices: FieldAttributeNode[];
}

export const UniversalCriteriaPlainComponent = (
  props: UniversalCriteriaPlainComponentProps,
): React.ReactElement => {
  const { isEdit, rules } = props;
  const [isOpen, setOpen] = React.useState(false);
  const { t } = useTranslation();
  return (
    <Box display='flex' flexDirection='column'>
      {isEdit && (
        <>
          {!!rules.length && (
            <Box
              mb={2}
              display='flex'
              alignItems='flex-end'
              justify-content='flex-end'
            >
              <Button
                variant='outlined'
                color='primary'
                onClick={() => setOpen(true)}
                data-cy='add-filter-button'
              >
                {t('Add')} &apos;Or&apos; {t('Filter')}
              </Button>
            </Box>
          )}
        </>
      )}
      <UniversalCriteriaComponent
        {...props}
        isAddDialogOpen={isOpen}
        onAddDialogClose={() => setOpen(false)}
      />
    </Box>
  );
};
