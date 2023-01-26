import { Button, Paper, Typography } from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { FieldAttributeNode } from '../../../__generated__/graphql';
import { UniversalCriteriaComponent } from './UniversalCriteriaComponent';

export const ContentWrapper = styled.div`
  display: flex;
  flex-wrap: wrap;
  padding: ${({ theme }) => theme.spacing(4)}px
    ${({ theme }) => theme.spacing(4)}px;
`;

const PaperContainer = styled(Paper)`
  margin: ${({ theme }) => theme.spacing(5)}px;
  border-bottom: 1px solid rgba(224, 224, 224, 1);
`;

const Title = styled.div`
  padding: ${({ theme }) => theme.spacing(3)}px
    ${({ theme }) => theme.spacing(4)}px;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

interface UniversalCriteriaPaperComponentProps {
  rules?;
  arrayHelpers?;
  individualDataNeeded?: boolean;
  isEdit?: boolean;
  individualFieldsChoices: FieldAttributeNode[];
  householdFieldsChoices: FieldAttributeNode[];
  title: string;
  disabled?: boolean;
}

export const UniversalCriteriaPaperComponent = (
  props: UniversalCriteriaPaperComponentProps,
): React.ReactElement => {
  const { title, isEdit, rules } = props;
  const { t } = useTranslation();
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [isOpen, setOpen] = useState(false);

  return (
    <div>
      <PaperContainer>
        <Title>
          <Typography variant='h6'>{title}</Typography>
          {isEdit && (
            <>
              {!!rules.length && (
                <Button
                  variant='outlined'
                  color='primary'
                  onClick={() => setOpen(true)}
                >
                  {t('Add')} &apos;Or&apos; {t('Filter')}
                </Button>
              )}
            </>
          )}
        </Title>
        <UniversalCriteriaComponent
          {...props}
          isAddDialogOpen={isOpen}
          onAddDialogClose={() => setOpen(false)}
        />
      </PaperContainer>
    </div>
  );
};
